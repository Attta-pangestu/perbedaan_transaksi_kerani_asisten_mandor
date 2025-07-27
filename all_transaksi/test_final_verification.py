#!/usr/bin/env python3
"""
Script Test Final untuk Memverifikasi Logika Perbedaan Input
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

def test_original_logic(connector, start_date, end_date, employee_mapping, limit=10):
    """
    Test logika dari analisis_perbedaan_panen.py
    """
    print("=== TEST LOGIKA ORIGINAL (analisis_perbedaan_panen.py) ===")
    
    # Determine the correct table name based on the month
    month_num = int(start_date.split('-')[1])
    ffb_table = f"FFBSCANNERDATA{month_num:02d}"
    
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

    # Batasi untuk test
    if limit and len(duplicate_transnos) > limit:
        duplicate_transnos = duplicate_transnos[:limit]

    # Firebird 1.5 has a limit of 1500 values in an IN clause
    BATCH_SIZE = 1000
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

        batch_result = connector.execute_query(query)
        all_results.extend(batch_result)

    # Convert to pandas DataFrame
    df = connector.to_pandas(all_results)
    
    if df.empty:
        return pd.DataFrame()

    # Group by TRANSNO and TRANSDATE
    grouped = df.groupby(['TRANSNO', 'TRANSDATE'])
    results = []

    # Proses setiap grup
    for group_key, group in grouped:
        transno = group_key[0]
        transdate = group_key[1]
        
        # Skip jika hanya ada satu record
        if len(group) <= 1:
            continue

        # Pisahkan berdasarkan RECORDTAG
        pm_records = group[group['RECORDTAG'] == 'PM']
        p1_records = group[group['RECORDTAG'] == 'P1']
        p5_records = group[group['RECORDTAG'] == 'P5']

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
            'TRANSNO': transno,
            'TRANSDATE': transdate
        }

        # Tambahkan kolom user
        user_id_1 = str(record1['SCANUSERID']).strip() if record1['SCANUSERID'] else ''
        user_id_2 = str(record2['SCANUSERID']).strip() if record2['SCANUSERID'] else ''

        # Tambahkan nama karyawan
        if employee_mapping:
            result['NAME_1'] = employee_mapping.get(user_id_1, f"KARYAWAN-{user_id_1}")
            result['NAME_2'] = employee_mapping.get(user_id_2, f"KARYAWAN-{user_id_2}")

        # Hitung perbedaan untuk setiap kolom perbandingan
        differences_count = 0
        fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
        
        for field in fields_to_compare:
            value1 = float(record1[field]) if record1[field] else 0
            value2 = float(record2[field]) if record2[field] else 0

            result[f'{field}_1'] = value1
            result[f'{field}_2'] = value2
            result[f'{field}_DIFF'] = value2 - value1
            
            if value1 != value2:
                differences_count += 1

        result['DIFFERENCES_COUNT'] = differences_count
        results.append(result)

    # Convert results to DataFrame
    if not results:
        return pd.DataFrame()

    df_results = pd.DataFrame(results)
    return df_results

def test_gui_logic(connector, start_date, end_date, employee_mapping, limit=10):
    """
    Test logika dari gui_multi_estate_ffb_analysis.py
    """
    print("=== TEST LOGIKA GUI MULTI-ESTATE ===")
    
    start_str = start_date
    end_str = end_date
    month_num = int(start_date.split('-')[1])
    ffb_table = f"FFBSCANNERDATA{month_num:02d}"
    
    # Query untuk mendapatkan data granular untuk analisis duplikat - SAMA DENGAN analisis_perbedaan_panen.py
    query = f"""
    SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
           a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
           a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
           a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
           a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
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
        
        # Hitung data Kerani berdasarkan duplikat dan perbedaan input - MENGGUNAKAN LOGIKA SAMA DENGAN analisis_perbedaan_panen.py
        kerani_df = df[df['RECORDTAG'] == 'PM']
        if not kerani_df.empty:
            for user_id, group in kerani_df.groupby('SCANUSERID'):
                user_id_str = str(user_id).strip()
                
                # Hitung jumlah perbedaan input untuk transaksi yang terverifikasi - MENGGUNAKAN LOGIKA SAMA DENGAN analisis_perbedaan_panen.py
                for _, kerani_row in group.iterrows():
                    if kerani_row['TRANSNO'] in verified_transnos:
                        # Cari transaksi dengan TRANSNO yang sama tapi RECORDTAG berbeda
                        matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) & 
                                                  (df['RECORDTAG'] != 'PM')]
                        if not matching_transactions.empty:
                            # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor) - SAMA DENGAN analisis_perbedaan_panen.py
                            p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                            p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']
                            
                            if not p1_records.empty:
                                other_row = p1_records.iloc[0]
                            else:
                                other_row = p5_records.iloc[0]
                            
                            # Hitung perbedaan untuk setiap field - MENGGUNAKAN LOGIKA SAMA DENGAN analisis_perbedaan_panen.py
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

def compare_results_detailed(original_results, gui_results):
    """
    Membandingkan hasil dari kedua metode secara detail
    """
    print("\n=== PERBANDINGAN HASIL DETAIL ===")
    
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
            
            for transno in list(common_transnos):
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
                    
                    # Show detailed field comparison for mismatches
                    fields = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                    for field in fields:
                        orig_diff_field = orig_row.get(f'{field}_DIFF', 0)
                        gui_diff_field = gui_row.get(f'{field}_DIFF', 0)
                        if orig_diff_field != gui_diff_field:
                            print(f"    {field}: Original={orig_diff_field}, GUI={gui_diff_field}")
            
            print(f"\nSummary: {matches} matches, {mismatches} mismatches")
            
            if matches == len(common_transnos):
                print("✅ PERFECT MATCH! Both methods produce identical results.")
            else:
                print("❌ MISMATCHES FOUND! Methods produce different results.")

def main():
    """
    Fungsi utama untuk menjalankan test final
    """
    print("=== TEST FINAL VERIFIKASI LOGIKA PERBEDAAN INPUT ===")
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
        limit = 10  # Limit untuk test
        
        # Get employee mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"✓ Employee mapping: {len(employee_mapping)} employees")
        
        # Test original method
        print("\n" + "="*60)
        original_results = test_original_logic(connector, start_date, end_date, employee_mapping, limit)
        
        # Test GUI method
        print("\n" + "="*60)
        gui_results = test_gui_logic(connector, start_date, end_date, employee_mapping, limit)
        
        # Compare results
        print("\n" + "="*60)
        compare_results_detailed(original_results, gui_results)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    main() 