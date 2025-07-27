#!/usr/bin/env python3
"""
Script Test untuk Memverifikasi dan Membandingkan Logika Perbedaan Input
antara analisis_perbedaan_panen.py dan gui_multi_estate_ffb_analysis.py
"""

import os
import sys
import pandas as pd
from datetime import date
from firebird_connector import FirebirdConnector

def get_employee_mapping(connector):
    """Mendapatkan mapping employee dari database"""
    query = "SELECT ID, NAME FROM EMP"
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        mapping = {}
        if not df.empty:
            for _, row in df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                mapping[emp_id] = emp_name
        return mapping
    except:
        return {}

def get_duplicate_transno_data_original(connector, start_date, end_date, limit=None):
    """
    Menggunakan logika dari analisis_perbedaan_panen.py untuk mendapatkan data duplikat
    """
    print("=== MENGAMBIL DATA DENGAN LOGIKA ORIGINAL (analisis_perbedaan_panen.py) ===")
    
    # Determine the correct table name based on the month
    month_num = int(start_date.split('-')[1])
    ffb_table = f"FFBSCANNERDATA{month_num:02d}"
    print(f"Using table {ffb_table} for month {month_num}")

    # Simplified query that finds TRANSNOs with multiple records on the same date
    transno_query = f"""
    SELECT a.TRANSNO, COUNT(*) AS JUMLAH
    FROM {ffb_table} a
    WHERE a.TRANSDATE >= '{start_date}' AND a.TRANSDATE < '{end_date}'
    GROUP BY a.TRANSNO
    HAVING COUNT(*) > 1
    """

    transno_result = connector.execute_query(transno_query)
    transno_df = connector.to_pandas(transno_result)

    if transno_df.empty:
        print("Tidak ditemukan TRANSNO duplikat.")
        return pd.DataFrame()

    # Dapatkan daftar TRANSNO yang duplikat
    duplicate_transnos = transno_df['TRANSNO'].tolist()
    print(f"Ditemukan {len(duplicate_transnos)} TRANSNO duplikat.")

    # Jika ada batasan, batasi jumlahnya untuk query yang lebih cepat
    if limit and len(duplicate_transnos) > limit:
        print(f"Membatasi analisis untuk {limit} TRANSNO pertama dari {len(duplicate_transnos)} total.")
        duplicate_transnos = duplicate_transnos[:limit]

    # Firebird 1.5 has a limit of 1500 values in an IN clause
    # Split the query into smaller batches
    BATCH_SIZE = 1000  # Safely under the 1500 limit
    all_results = []

    # Process in batches
    for i in range(0, len(duplicate_transnos), BATCH_SIZE):
        batch = duplicate_transnos[i:i+BATCH_SIZE]
        transno_list = ", ".join([f"'{tn}'" for tn in batch])

        query = f"""
        SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
               a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
               a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
               a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
               a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
        FROM {ffb_table} a
        WHERE a.TRANSNO IN ({transno_list})
        AND a.TRANSDATE >= '{start_date}' AND a.TRANSDATE < '{end_date}'
        ORDER BY a.TRANSNO, a.TRANSDATE
        """

        print(f"Executing query batch {i//BATCH_SIZE + 1} with {len(batch)} TRANSNO values...")
        batch_result = connector.execute_query(query)
        all_results.extend(batch_result)

    print(f"Total records retrieved: {len(all_results)}")

    # Convert to pandas DataFrame
    df = connector.to_pandas(all_results)
    return df

def analyze_differences_original(df, employee_mapping):
    """
    Menggunakan logika dari analisis_perbedaan_panen.py untuk menganalisis perbedaan
    """
    print("=== ANALISIS PERBEDAAN DENGAN LOGIKA ORIGINAL ===")
    
    if df.empty:
        print("No data to analyze.")
        return pd.DataFrame(), {}

    # Periksa dan perbaiki nama kolom
    print("Kolom yang tersedia dalam data:")
    for col in df.columns:
        print(f"  - {col}")

    # Cari kolom TRANSNO
    transno_col = None
    if 'TRANSNO' in df.columns:
        transno_col = 'TRANSNO'
        print(f"Menggunakan kolom TRANSNO sebagai TRANSNO")
    else:
        for col in df.columns:
            if 'TRANSNO' in col.upper():
                transno_col = col
                print(f"Menggunakan kolom {col} sebagai TRANSNO")
                break

    if not transno_col:
        print("Tidak dapat menemukan kolom TRANSNO.")
        return pd.DataFrame(), {}

    # Cari kolom tanggal
    transdate_col = None
    if 'TRANSDATE' in df.columns:
        transdate_col = 'TRANSDATE'
        print(f"Menggunakan kolom TRANSDATE sebagai TRANSDATE")
    else:
        for col in df.columns:
            if 'DATE' in col.upper() and not transdate_col:
                transdate_col = col
                print(f"Menggunakan kolom {col} sebagai TRANSDATE")
                break

    # Cari kolom yang akan dibandingkan
    comparison_mapping = {
        'RIPEBCH': None,
        'UNRIPEBCH': None,
        'BLACKBCH': None,
        'ROTTENBCH': None,
        'LONGSTALKBCH': None,
        'RATDMGBCH': None,
        'LOOSEFRUIT': None
    }

    # Mapping manual berdasarkan output isql yang kita lihat
    manual_mapping = {
        'RIPEBCH': 'RIPE',
        'UNRIPEBCH': 'CH    UNRIPE',
        'BLACKBCH': 'CH     BLACK',
        'ROTTENBCH': 'CH    ROTTEN',
        'LONGSTALKBCH': 'CH LONGSTALK',
        'RATDMGBCH': 'CH    RATDMG',
        'LOOSEFRUIT': 'CH   LOOSEFR'
    }

    # Coba gunakan mapping manual terlebih dahulu
    for target_col, mapped_col in manual_mapping.items():
        if mapped_col in df.columns:
            comparison_mapping[target_col] = mapped_col
            print(f"Menggunakan kolom {mapped_col} sebagai {target_col} (manual mapping)")

    # Jika masih ada yang belum ter-mapping, coba dengan cara otomatis
    for target_col in comparison_mapping.keys():
        if comparison_mapping[target_col] is None:
            for col in df.columns:
                if target_col.upper() in col.upper():
                    comparison_mapping[target_col] = col
                    print(f"Menggunakan kolom {col} sebagai {target_col} (auto mapping)")
                    break

    # Kolom yang akan dibandingkan (yang ditemukan)
    comparison_columns = [col for col, mapped in comparison_mapping.items() if mapped]

    # Pastikan kolom numerik
    for col in comparison_columns:
        mapped_col = comparison_mapping[col]
        if mapped_col in df.columns:
            df[mapped_col] = pd.to_numeric(df[mapped_col], errors='coerce').fillna(0)

    # Cari kolom SCANUSERID
    scanuserid_col = None
    if 'SCANUSERID' in df.columns:
        scanuserid_col = 'SCANUSERID'
        print(f"Menggunakan kolom SCANUSERID sebagai SCANUSERID")
    else:
        for col in df.columns:
            if 'SCANUSER' in col.upper() or 'USER' in col.upper():
                scanuserid_col = col
                print(f"Menggunakan kolom {col} sebagai SCANUSERID")
                break

    # Cari kolom RECORDTAG
    recordtag_col = None
    if 'RECORDTAG' in df.columns:
        recordtag_col = 'RECORDTAG'
        print(f"Menggunakan kolom RECORDTAG sebagai RECORDTAG")
    else:
        for col in df.columns:
            if 'RECORDTAG' in col.upper() or 'TAG' in col.upper():
                recordtag_col = col
                print(f"Menggunakan kolom {col} sebagai RECORDTAG")
                break

    # Group by TRANSNO and TRANSDATE
    if transdate_col:
        print(f"Grouping by both {transno_col} and {transdate_col}")
        grouped = df.groupby([transno_col, transdate_col])
    else:
        print(f"Warning: No TRANSDATE column found, grouping only by {transno_col}")
        grouped = df.groupby(transno_col)

    # Initialize list untuk menyimpan hasil
    results = []

    # Proses setiap grup
    for group_key, group in grouped:
        # Extract transno (and transdate if available)
        if isinstance(group_key, tuple):
            transno = group_key[0]
            transdate = group_key[1] if len(group_key) > 1 else None
        else:
            transno = group_key
            transdate = None
            
        # Skip jika hanya ada satu record
        if len(group) <= 1:
            continue

        # Pisahkan berdasarkan RECORDTAG
        pm_records = group[group[recordtag_col] == 'PM']
        p1_records = group[group[recordtag_col] == 'P1']
        p5_records = group[group[recordtag_col] == 'P5']

        # Jika tidak ada record PM, skip
        if pm_records.empty:
            continue
        # Jika tidak ada record P1 atau P5, skip
        elif p1_records.empty and p5_records.empty:
            continue
        else:
            # Ambil record PM sebagai record1 (Kerani)
            record1 = pm_records.iloc[0]

            # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
            if not p1_records.empty:
                record2 = p1_records.iloc[0]
            else:
                record2 = p5_records.iloc[0]

        # Buat dictionary hasil dasar
        result = {
            'TRANSNO': transno
        }

        # Tambahkan kolom tanggal jika tersedia dari grouping
        if transdate:
            result['TRANSDATE'] = transdate
        elif transdate_col:
            result['TRANSDATE'] = record1[transdate_col]

        # Tambahkan kolom user jika tersedia
        if scanuserid_col:
            user_id_1 = str(record1[scanuserid_col]).strip() if record1[scanuserid_col] else ''
            user_id_2 = str(record2[scanuserid_col]).strip() if record2[scanuserid_col] else ''

            # Tambahkan nama karyawan
            if employee_mapping:
                result['NAME_1'] = employee_mapping.get(user_id_1, f"KARYAWAN-{user_id_1}")
                result['NAME_2'] = employee_mapping.get(user_id_2, f"KARYAWAN-{user_id_2}")

        # Hitung perbedaan untuk setiap kolom perbandingan
        differences_count = 0
        for col in comparison_columns:
            mapped_col = comparison_mapping[col]
            if mapped_col in record1 and mapped_col in record2:
                value1 = float(record1[mapped_col]) if record1[mapped_col] else 0
                value2 = float(record2[mapped_col]) if record2[mapped_col] else 0

                result[f'{col}_1'] = value1
                result[f'{col}_2'] = value2
                result[f'{col}_DIFF'] = value2 - value1
                
                if value1 != value2:
                    differences_count += 1

        result['DIFFERENCES_COUNT'] = differences_count
        results.append(result)

    # Convert results to DataFrame
    if not results:
        return pd.DataFrame(), {}

    df_results = pd.DataFrame(results)
    return df_results

def analyze_differences_gui_style(connector, start_date, end_date, employee_mapping):
    """
    Menggunakan logika dari gui_multi_estate_ffb_analysis.py untuk menganalisis perbedaan
    """
    print("=== ANALISIS PERBEDAAN DENGAN LOGIKA GUI MULTI-ESTATE ===")
    
    start_str = start_date
    end_str = end_date
    month_num = int(start_date.split('-')[1])
    ffb_table = f"FFBSCANNERDATA{month_num:02d}"
    
    # Query untuk mendapatkan data granular untuk analisis duplikat
    query = f"""
    SELECT a.SCANUSERID, a.RECORDTAG, a.TRANSNO, a.TRANSDATE, 
           a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, 
           a.LONGSTALKBCH, a.RATDMGBCH, a.LOOSEFRUIT
    FROM {ffb_table} a
    WHERE a.TRANSDATE >= '{start_str}' 
        AND a.TRANSDATE <= '{end_str}'
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            return pd.DataFrame()
        
        # Logika dari analisis_perbedaan_panen.py: cari duplikat berdasarkan TRANSNO
        duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())

        results = []
        
        # Hitung data Kerani berdasarkan duplikat dan perbedaan input
        kerani_df = df[df['RECORDTAG'] == 'PM']
        if not kerani_df.empty:
            for user_id, group in kerani_df.groupby('SCANUSERID'):
                user_id_str = str(user_id).strip()
                
                # Hitung jumlah perbedaan input untuk transaksi yang terverifikasi
                for _, kerani_row in group.iterrows():
                    if kerani_row['TRANSNO'] in verified_transnos:
                        # Cari transaksi dengan TRANSNO yang sama tapi RECORDTAG berbeda
                        matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) & 
                                                  (df['RECORDTAG'] != 'PM')]
                        if not matching_transactions.empty:
                            # Ambil transaksi pertama yang bukan PM
                            other_row = matching_transactions.iloc[0]
                            
                            # Hitung perbedaan untuk setiap field
                            fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 
                                               'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                            
                            differences_count = 0
                            result = {
                                'TRANSNO': kerani_row['TRANSNO'],
                                'TRANSDATE': kerani_row['TRANSDATE'],
                                'NAME_1': employee_mapping.get(user_id_str, f"EMP-{user_id_str}"),
                                'NAME_2': employee_mapping.get(str(other_row['SCANUSERID']).strip(), f"EMP-{other_row['SCANUSERID']}")
                            }
                            
                            for field in fields_to_compare:
                                try:
                                    kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                                    other_val = float(other_row[field]) if other_row[field] else 0
                                    result[f'{field}_1'] = kerani_val
                                    result[f'{field}_2'] = other_val
                                    result[f'{field}_DIFF'] = other_val - kerani_val
                                    if kerani_val != other_val:
                                        differences_count += 1
                                except:
                                    result[f'{field}_1'] = 0
                                    result[f'{field}_2'] = 0
                                    result[f'{field}_DIFF'] = 0
                            
                            result['DIFFERENCES_COUNT'] = differences_count
                            results.append(result)
        
        return pd.DataFrame(results)
        
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def compare_results(original_results, gui_results):
    """
    Membandingkan hasil dari kedua metode
    """
    print("\n=== PERBANDINGAN HASIL ===")
    
    print(f"Original method results: {len(original_results)} records")
    print(f"GUI method results: {len(gui_results)} records")
    
    if original_results.empty and gui_results.empty:
        print("Both methods returned empty results")
        return
    
    if original_results.empty:
        print("Original method returned empty results")
        return
    
    if gui_results.empty:
        print("GUI method returned empty results")
        return
    
    # Compare by TRANSNO
    original_transnos = set(original_results['TRANSNO'].tolist())
    gui_transnos = set(gui_results['TRANSNO'].tolist())
    
    print(f"\nTRANSNO comparison:")
    print(f"Original method unique TRANSNOs: {len(original_transnos)}")
    print(f"GUI method unique TRANSNOs: {len(gui_transnos)}")
    print(f"Common TRANSNOs: {len(original_transnos.intersection(gui_transnos))}")
    print(f"Only in original: {len(original_transnos - gui_transnos)}")
    print(f"Only in GUI: {len(gui_transnos - original_transnos)}")
    
    # Compare differences count
    if 'DIFFERENCES_COUNT' in original_results.columns and 'DIFFERENCES_COUNT' in gui_results.columns:
        print(f"\nDifferences count comparison:")
        
        # Get common TRANSNOs
        common_transnos = original_transnos.intersection(gui_transnos)
        
        if common_transnos:
            print(f"Comparing {len(common_transnos)} common TRANSNOs:")
            
            matches = 0
            mismatches = 0
            
            for transno in list(common_transnos)[:10]:  # Compare first 10
                orig_row = original_results[original_results['TRANSNO'] == transno].iloc[0]
                gui_row = gui_results[gui_results['TRANSNO'] == transno].iloc[0]
                
                orig_diff = orig_row['DIFFERENCES_COUNT']
                gui_diff = gui_row['DIFFERENCES_COUNT']
                
                if orig_diff == gui_diff:
                    matches += 1
                    print(f"  TRANSNO {transno}: ✓ Match ({orig_diff} differences)")
                else:
                    mismatches += 1
                    print(f"  TRANSNO {transno}: ✗ Mismatch (Original: {orig_diff}, GUI: {gui_diff})")
            
            print(f"\nSummary: {matches} matches, {mismatches} mismatches")
            
            if mismatches > 0:
                print("\n=== DETAILED ANALYSIS OF MISMATCHES ===")
                for transno in list(common_transnos)[:5]:  # Analyze first 5 mismatches
                    orig_row = original_results[original_results['TRANSNO'] == transno].iloc[0]
                    gui_row = gui_results[gui_results['TRANSNO'] == transno].iloc[0]
                    
                    print(f"\nTRANSNO {transno}:")
                    print(f"  Original method: {orig_row['DIFFERENCES_COUNT']} differences")
                    print(f"  GUI method: {gui_row['DIFFERENCES_COUNT']} differences")
                    
                    # Show field-by-field comparison
                    fields = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                    for field in fields:
                        orig_diff = orig_row.get(f'{field}_DIFF', 0)
                        gui_diff = gui_row.get(f'{field}_DIFF', 0)
                        if orig_diff != gui_diff:
                            print(f"    {field}: Original={orig_diff}, GUI={gui_diff}")

def main():
    """
    Fungsi utama untuk menjalankan test
    """
    print("=== TEST PERBANDINGAN LOGIKA PERBEDAAN INPUT ===")
    print("Membandingkan analisis_perbedaan_panen.py vs gui_multi_estate_ffb_analysis.py")
    print()
    
    # Test database path
    test_db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    if not os.path.exists(test_db_path):
        print(f"Database tidak ditemukan: {test_db_path}")
        return False
    
    try:
        connector = FirebirdConnector(test_db_path)
        if not connector.test_connection():
            print("Gagal terhubung ke database")
            return False
        
        print("✓ Koneksi database berhasil")
        
        # Test parameters
        start_date = "2025-04-01"
        end_date = "2025-04-30"
        limit = 50  # Limit untuk test
        
        # Get employee mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"✓ Employee mapping: {len(employee_mapping)} employees")
        
        # Test original method
        print("\n" + "="*60)
        original_data = get_duplicate_transno_data_original(connector, start_date, end_date, limit)
        original_results = analyze_differences_original(original_data, employee_mapping)
        
        # Test GUI method
        print("\n" + "="*60)
        gui_results = analyze_differences_gui_style(connector, start_date, end_date, employee_mapping)
        
        # Compare results
        print("\n" + "="*60)
        compare_results(original_results, gui_results)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    main() 