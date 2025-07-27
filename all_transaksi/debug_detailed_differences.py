#!/usr/bin/env python3
"""
Debug detail untuk melihat mengapa tidak ada perbedaan yang terdeteksi
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import date
import pandas as pd

def debug_detailed_differences():
    """Debug detail perbedaan"""
    
    print("=== DEBUG DETAIL PERBEDAAN ===\n")
    
    # Koneksi ke database Estate 1A
    db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    try:
        connector = FirebirdConnector(db_path)
        if not connector.test_connection():
            print("❌ Koneksi database gagal")
            return
        
        print("✅ Koneksi database berhasil")
        
        # Get employee mapping
        emp_query = "SELECT ID, NAME FROM EMP"
        emp_result = connector.execute_query(emp_query)
        emp_df = connector.to_pandas(emp_result)
        employee_mapping = {}
        if not emp_df.empty:
            for _, row in emp_df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                employee_mapping[emp_id] = emp_name
        
        # Analisis data Mei 2025
        start_date = '2025-05-01'
        end_date = '2025-05-31'
        month_num = 5
        ffb_table = f"FFBSCANNERDATA{month_num:02d}"
        
        # Query untuk mendapatkan semua data
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
        
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        print(f"📊 Total records: {len(df)}")
        
        # Cari duplikat TRANSNO
        duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())
        print(f"✅ Transaksi duplikat ditemukan: {len(verified_transnos)} TRANSNO")
        
        # Analisis transaksi duplikat yang melibatkan Kerani target
        target_employees = {
            '183': 'DJULI DARTA ( ADDIANI )',
            '4771': 'ERLY ( MARDIAH )',
            '4201': 'IRWANSYAH ( Agustina )',
            '112': 'ZULHARI ( AMINAH )'
        }
        
        print(f"\n🔍 ANALISIS DETAIL TRANSAKSI DUPLIKAT:")
        
        total_differences = 0
        for emp_id, emp_name in target_employees.items():
            print(f"\n👤 {emp_name} (ID: {emp_id}):")
            
            # Cari transaksi Kerani untuk employee ini
            kerani_transactions = df[(df['SCANUSERID'] == int(emp_id)) & (df['RECORDTAG'] == 'PM')]
            print(f"  Total transaksi Kerani: {len(kerani_transactions)}")
            
            # Transaksi Kerani yang duplikat
            kerani_verified = kerani_transactions[kerani_transactions['TRANSNO'].isin(verified_transnos)]
            print(f"  Transaksi Kerani terverifikasi (duplikat): {len(kerani_verified)}")
            
            # Analisis setiap transaksi duplikat
            differences_count = 0
            sample_count = 0
            
            for _, kerani_row in kerani_verified.iterrows():
                if sample_count >= 10:  # Batasi sample untuk readability
                    break
                    
                transno = kerani_row['TRANSNO']
                
                # Cari transaksi matching dengan TRANSNO yang sama
                matching_transactions = df[(df['TRANSNO'] == transno) & (df['RECORDTAG'] != 'PM')]
                
                # Filter hanya yang memiliki TRANSSTATUS 704
                matching_704 = matching_transactions[matching_transactions['TRANSSTATUS'] == '704']
                
                print(f"\n    TRANSNO {transno}:")
                print(f"      Kerani status: {kerani_row['TRANSSTATUS']}")
                print(f"      Matching transactions: {len(matching_transactions)}")
                print(f"      Matching dengan status 704: {len(matching_704)}")
                
                if len(matching_704) > 0:
                    # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
                    p1_records = matching_704[matching_704['RECORDTAG'] == 'P1']
                    p5_records = matching_704[matching_704['RECORDTAG'] == 'P5']
                    
                    if not p1_records.empty:
                        other_row = p1_records.iloc[0]
                        print(f"      Menggunakan P1 (Asisten): {employee_mapping.get(str(other_row['SCANUSERID']).strip(), other_row['SCANUSERID'])}")
                    elif not p5_records.empty:
                        other_row = p5_records.iloc[0]
                        print(f"      Menggunakan P5 (Mandor): {employee_mapping.get(str(other_row['SCANUSERID']).strip(), other_row['SCANUSERID'])}")
                    else:
                        print(f"      Tidak ada P1 atau P5 dengan status 704")
                        continue
                    
                    # Hitung perbedaan untuk setiap field
                    fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 
                                       'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                    
                    field_differences = 0
                    print(f"      Perbandingan field:")
                    for field in fields_to_compare:
                        try:
                            kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                            other_val = float(other_row[field]) if other_row[field] else 0
                            if kerani_val != other_val:
                                field_differences += 1
                                print(f"        {field}: Kerani={kerani_val}, Other={other_val} ✅ BEDA")
                            else:
                                print(f"        {field}: Kerani={kerani_val}, Other={other_val} ❌ SAMA")
                        except Exception as e:
                            print(f"        {field}: Error - {e}")
                            continue
                    
                    differences_count += field_differences
                    print(f"      Total perbedaan field untuk TRANSNO ini: {field_differences}")
                    sample_count += 1
                else:
                    # Tampilkan detail mengapa tidak ada matching dengan status 704
                    if len(matching_transactions) > 0:
                        print(f"      Detail matching transactions:")
                        for _, match_row in matching_transactions.iterrows():
                            user_name = employee_mapping.get(str(match_row['SCANUSERID']).strip(), match_row['SCANUSERID'])
                            print(f"        {match_row['RECORDTAG']} | Status: {match_row['TRANSSTATUS']} | User: {user_name}")
                    else:
                        print(f"      Tidak ada matching transactions sama sekali")
            
            print(f"\n  TOTAL PERBEDAAN untuk {emp_name}: {differences_count}")
            total_differences += differences_count
        
        print(f"\n📊 TOTAL PERBEDAAN KESELURUHAN: {total_differences}")
        print(f"📊 TARGET PERBEDAAN: 111")
        
        if total_differences > 0:
            print(f"✅ Ditemukan perbedaan!")
        else:
            print(f"❌ Tidak ada perbedaan ditemukan - perlu investigasi lebih lanjut")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_detailed_differences() 