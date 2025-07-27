#!/usr/bin/env python3
"""
Test script untuk memverifikasi filter TRANSSTATUS 704 
menghasilkan hasil yang sesuai dengan data pembanding untuk Estate 1A bulan Mei 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import date
import pandas as pd

def get_employee_mapping(connector):
    """Mendapatkan mapping employee ID ke nama"""
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

def test_transstatus_704_filter():
    """Test filter TRANSSTATUS 704 untuk Estate 1A bulan Mei 2025"""
    
    # Target employees berdasarkan ID yang ditemukan
    target_employees = {
        '183': 'DJULI DARTA ( ADDIANI )',      # Expected: 40 differences
        '4771': 'ERLY ( MARDIAH )',            # Expected: 71 differences  
        '4201': 'IRWANSYAH ( Agustina )',      # Expected: 0 differences
        '112': 'ZULHARI ( AMINAH )'            # Expected: 0 differences
    }
    
    expected_differences = {
        '183': 40,   # DJULI DARTA
        '4771': 71,  # ERLY 
        '4201': 0,   # IRWANSYAH
        '112': 0     # ZULHARI
    }
    
    print("=== TEST FILTER TRANSSTATUS 704 UNTUK ESTATE 1A MEI 2025 ===\n")
    
    # Koneksi ke database Estate 1A
    db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    if not os.path.exists(db_path):
        print(f"❌ Database tidak ditemukan: {db_path}")
        return False
    
    try:
        connector = FirebirdConnector(db_path)
        if not connector.test_connection():
            print("❌ Koneksi database gagal")
            return False
        
        print("✅ Koneksi database berhasil")
        
        # Get employee mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"✅ Employee mapping: {len(employee_mapping)} entries")
        
        # Analisis dengan filter TRANSSTATUS 704
        start_date = '2025-05-01'
        end_date = '2025-05-31'
        month_num = 5
        ffb_table = f"FFBSCANNERDATA{month_num:02d}"
        
        # Query untuk mendapatkan semua data Estate 1A bulan Mei
        query = f"""
        SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
               a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
               a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
               a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
               a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
        FROM {ffb_table} a
        WHERE a.TRANSDATE >= '{start_date}' 
            AND a.TRANSDATE <= '{end_date}'
        """
        
        print(f"📊 Mengambil data dari {ffb_table} periode {start_date} - {end_date}")
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            print("❌ Tidak ada data ditemukan")
            return False
        
        print(f"✅ Data ditemukan: {len(df)} records")
        
        # Analisis perbedaan dengan filter TRANSSTATUS 704
        print("\n📈 ANALISIS PERBEDAAN DENGAN FILTER TRANSSTATUS 704:")
        
        # Cari duplikat TRANSNO
        duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())
        print(f"✅ Transaksi duplikat ditemukan: {len(verified_transnos)} TRANSNO")
        
        # Analisis per karyawan Kerani
        kerani_df = df[df['RECORDTAG'] == 'PM']
        print(f"✅ Transaksi Kerani ditemukan: {len(kerani_df)} records")
        
        results = {}
        
        for user_id, group in kerani_df.groupby('SCANUSERID'):
            user_id_str = str(user_id).strip()
            user_name = employee_mapping.get(user_id_str, f"KARYAWAN-{user_id_str}")
            
            total_created = len(group)
            differences_count = 0
            
            # Hitung perbedaan dengan filter TRANSSTATUS 704
            for _, kerani_row in group.iterrows():
                if kerani_row['TRANSNO'] in verified_transnos:
                    # Cari transaksi matching dengan TRANSSTATUS 704 (hanya untuk Mandor/Asisten)
                    matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) & 
                                              (df['RECORDTAG'] != 'PM') &
                                              (df['TRANSSTATUS'] == '704')]
                    
                    if not matching_transactions.empty:
                        # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
                        p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                        p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']
                        
                        if not p1_records.empty:
                            other_row = p1_records.iloc[0]
                        elif not p5_records.empty:
                            other_row = p5_records.iloc[0]
                        else:
                            continue
                        
                        # Hitung perbedaan untuk setiap field
                        fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 
                                           'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                        
                        for field in fields_to_compare:
                            try:
                                kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                                other_val = float(other_row[field]) if other_row[field] else 0
                                if kerani_val != other_val:
                                    differences_count += 1
                            except:
                                continue
            
            results[user_name] = {
                'total': total_created,
                'differences': differences_count
            }
        
        # Bandingkan dengan data pembanding
        print("\n🔍 PERBANDINGAN DENGAN DATA PEMBANDING:")
        print("=" * 80)
        print(f"{'Nama Karyawan':<40} {'Total':<8} {'Beda':<8} {'Expected':<12} {'Status':<10}")
        print("=" * 80)
        
        total_matches = 0
        total_employees = 0
        
        for emp_id, emp_name in target_employees.items():
            total_employees += 1
            expected_diff = expected_differences[emp_id]
            
            # Cari nama yang cocok dalam hasil
            found_match = False
            for result_name, result_data in results.items():
                # Cek apakah nama cocok (partial match)
                if emp_name in result_name or result_name in emp_name:
                    actual_total = result_data['total']
                    actual_diff = result_data['differences']
                    
                    # Cek apakah perbedaan cocok
                    diff_match = actual_diff == expected_diff
                    status = "✅ MATCH" if diff_match else "❌ MISMATCH"
                    
                    if diff_match:
                        total_matches += 1
                    
                    print(f"{emp_name[:39]:<40} {actual_total:<8} {actual_diff:<8} {expected_diff:<12} {status:<10}")
                    found_match = True
                    break
            
            if not found_match:
                print(f"{emp_name[:39]:<40} {'N/A':<8} {'N/A':<8} {expected_diff:<12} {'❌ NOT FOUND':<10}")
        
        print("=" * 80)
        print(f"HASIL: {total_matches}/{total_employees} karyawan cocok dengan data pembanding")
        
        # Tampilkan summary
        print(f"\n📊 SUMMARY HASIL FILTER TRANSSTATUS 704:")
        total_differences_calculated = sum(r['differences'] for r in results.values())
        total_differences_expected = sum(expected_differences.values())
        
        print(f"Total perbedaan yang dihitung: {total_differences_calculated}")
        print(f"Total perbedaan yang diharapkan: {total_differences_expected}")
        
        if total_differences_calculated == total_differences_expected:
            print("✅ TOTAL PERBEDAAN COCOK SEMPURNA!")
        else:
            print(f"❌ TOTAL PERBEDAAN TIDAK COCOK (selisih: {abs(total_differences_calculated - total_differences_expected)})")
        
        return total_matches == total_employees
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_transstatus_704_filter()
    if success:
        print("\n🎉 TEST BERHASIL: Filter TRANSSTATUS 704 menghasilkan hasil yang sesuai!")
    else:
        print("\n⚠️ TEST GAGAL: Hasil tidak sesuai dengan data pembanding") 