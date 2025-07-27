#!/usr/bin/env python3
"""
Debug script untuk menganalisis masalah dengan filter TRANSSTATUS 704
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import date
import pandas as pd

def debug_transstatus_704():
    """Debug filter TRANSSTATUS 704"""
    
    print("=== DEBUG FILTER TRANSSTATUS 704 ===\n")
    
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
        
        # Analisis TRANSSTATUS
        status_counts = df['TRANSSTATUS'].value_counts()
        print(f"\n📈 DISTRIBUSI TRANSSTATUS:")
        for status, count in status_counts.items():
            print(f"  {status}: {count} records")
        
        # Analisis RECORDTAG
        recordtag_counts = df['RECORDTAG'].value_counts()
        print(f"\n📈 DISTRIBUSI RECORDTAG:")
        for tag, count in recordtag_counts.items():
            print(f"  {tag}: {count} records")
        
        # Analisis kombinasi RECORDTAG + TRANSSTATUS
        combo_counts = df.groupby(['RECORDTAG', 'TRANSSTATUS']).size().reset_index(name='count')
        print(f"\n📈 KOMBINASI RECORDTAG + TRANSSTATUS:")
        for _, row in combo_counts.iterrows():
            print(f"  {row['RECORDTAG']} + {row['TRANSSTATUS']}: {row['count']} records")
        
        # Cari duplikat TRANSNO
        duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())
        print(f"\n🔍 DUPLIKAT TRANSNO:")
        print(f"  Total TRANSNO duplikat: {len(verified_transnos)}")
        
        # Analisis transaksi duplikat dengan TRANSSTATUS 704
        duplikat_704 = duplicated_rows[duplicated_rows['TRANSSTATUS'] == '704']
        print(f"  Duplikat dengan TRANSSTATUS 704: {len(duplikat_704)}")
        
        # Analisis per user untuk Kerani (PM)
        kerani_df = df[df['RECORDTAG'] == 'PM']
        print(f"\n👤 ANALISIS KERANI (PM):")
        print(f"  Total transaksi Kerani: {len(kerani_df)}")
        
        # Analisis Kerani dengan TRANSSTATUS 704
        kerani_704 = kerani_df[kerani_df['TRANSSTATUS'] == '704']
        print(f"  Kerani dengan TRANSSTATUS 704: {len(kerani_704)}")
        
        # Analisis per user Kerani
        for user_id, group in kerani_df.groupby('SCANUSERID'):
            user_id_str = str(user_id).strip()
            user_name = employee_mapping.get(user_id_str, f"KARYAWAN-{user_id_str}")
            
            # Filter berdasarkan nama yang diharapkan
            expected_names = ['DJULI DARTA ( ADDIANI )', 'ERLY ( MARDIAH )', 'IRWANSYAH ( Agustina )', 'ZULHARI ( AMINAH )']
            if any(expected in user_name for expected in expected_names):
                print(f"\n  👤 {user_name} (ID: {user_id_str}):")
                print(f"    Total transaksi: {len(group)}")
                
                # Transaksi dengan status 704
                group_704 = group[group['TRANSSTATUS'] == '704']
                print(f"    Transaksi dengan status 704: {len(group_704)}")
                
                # Transaksi yang terverifikasi (duplikat)
                verified_group = group[group['TRANSNO'].isin(verified_transnos)]
                print(f"    Transaksi terverifikasi (duplikat): {len(verified_group)}")
                
                # Transaksi terverifikasi dengan status 704
                verified_704 = verified_group[verified_group['TRANSSTATUS'] == '704']
                print(f"    Transaksi terverifikasi + status 704: {len(verified_704)}")
                
                # Analisis perbedaan
                differences_count = 0
                for _, kerani_row in verified_704.iterrows():
                    # Cari transaksi matching dengan TRANSSTATUS 704
                    matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) & 
                                              (df['RECORDTAG'] != 'PM') &
                                              (df['TRANSSTATUS'] == '704')]
                    
                    if not matching_transactions.empty:
                        print(f"      TRANSNO {kerani_row['TRANSNO']}: {len(matching_transactions)} matching transactions")
                        
                        # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor)
                        p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                        p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']
                        
                        if not p1_records.empty:
                            other_row = p1_records.iloc[0]
                            print(f"        Menggunakan P1 (Asisten) untuk perbandingan")
                        elif not p5_records.empty:
                            other_row = p5_records.iloc[0]
                            print(f"        Menggunakan P5 (Mandor) untuk perbandingan")
                        else:
                            print(f"        Tidak ada P1 atau P5 untuk perbandingan")
                            continue
                        
                        # Hitung perbedaan untuk setiap field
                        fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 
                                           'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                        
                        field_differences = 0
                        for field in fields_to_compare:
                            try:
                                kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                                other_val = float(other_row[field]) if other_row[field] else 0
                                if kerani_val != other_val:
                                    field_differences += 1
                                    print(f"        {field}: Kerani={kerani_val}, Other={other_val} (BEDA)")
                            except:
                                continue
                        
                        differences_count += field_differences
                        print(f"        Total perbedaan field untuk TRANSNO ini: {field_differences}")
                
                print(f"    TOTAL PERBEDAAN: {differences_count}")
        
        # Sample beberapa TRANSNO duplikat untuk analisis detail
        print(f"\n🔍 SAMPLE ANALISIS TRANSNO DUPLIKAT:")
        sample_transnos = list(verified_transnos)[:5]
        
        for transno in sample_transnos:
            transno_data = df[df['TRANSNO'] == transno]
            print(f"\n  TRANSNO {transno}:")
            print(f"    Total records: {len(transno_data)}")
            
            for _, row in transno_data.iterrows():
                print(f"    {row['RECORDTAG']} | Status: {row['TRANSSTATUS']} | User: {employee_mapping.get(str(row['SCANUSERID']).strip(), row['SCANUSERID'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_transstatus_704() 