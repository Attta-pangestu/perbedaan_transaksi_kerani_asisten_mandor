#!/usr/bin/env python3
"""
Script untuk menganalisis dan memperbaiki perhitungan MANDOR 
dengan logika yang akurat sesuai hasil crosscheck.
"""

import sys
import os
import pandas as pd
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), 'all_transaksi'))

from firebird_connector import FirebirdConnector
from analisis_per_karyawan import get_employee_mapping, get_employee_role_from_recordtag

def analyze_mandor_accurate():
    """
    Analisis MANDOR yang akurat berdasarkan hasil crosscheck
    """
    # Konfigurasi database
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    
    print("ANALISIS MANDOR YANG AKURAT")
    print("="*60)
    
    # Setup database connection
    print("Menghubungkan ke database...")
    connector = FirebirdConnector(DB_PATH)
    
    if not connector.test_connection():
        print("Koneksi database gagal!")
        return
    
    print("Koneksi database berhasil")
    
    # Load employee mapping
    employee_mapping = get_employee_mapping(connector)
    
    # Query untuk mengambil semua data MANDOR (P5) di bulan 05
    query = """
    SELECT 
        a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
        a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
        a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
        a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
        a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
        b.DIVID, c.DIVNAME, c.DIVCODE
    FROM FFBSCANNERDATA05 a
    LEFT JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID
    LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
    WHERE a.TRANSDATE >= '2025-05-01' 
    AND a.TRANSDATE < '2025-06-01'
    AND a.RECORDTAG = 'P5'
    ORDER BY a.SCANUSERID, a.TRANSDATE, a.TRANSTIME
    """
    
    print("\nMengambil data semua transaksi MANDOR (P5)...")
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df is not None and not df.empty:
            print(f"Total transaksi MANDOR (P5): {len(df)}")
            
            # Analisis per MANDOR
            mandor_stats = defaultdict(lambda: {
                'employee_id': '',
                'employee_name': '',
                'total_transactions': 0,
                'verified_transactions': 0,
                'divisions': set(),
                'transaction_details': []
            })
            
            # Column mapping
            scanuserid_col = 1   # SCANUSERID
            recordtag_col = 18   # RECORDTAG  
            transstatus_col = 19 # TRANSSTATUS
            transno_col = 14     # TRANSNO
            transdate_col = 15   # TRANSDATE
            divname_col = 28     # DIVNAME
            
            for _, row in df.iterrows():
                try:
                    creator_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
                    recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
                    transstatus = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else ''
                    transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
                    transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
                    division = str(row.iloc[divname_col]).strip() if pd.notna(row.iloc[divname_col]) else 'Unknown'
                    
                    if creator_id and recordtag == 'P5':
                        # Get employee name
                        if 'get_name' in employee_mapping:
                            creator_name = employee_mapping['get_name'](creator_id)
                        else:
                            creator_name = employee_mapping.get(creator_id, f"MANDOR-{creator_id}")
                        
                        mandor_stats[creator_id]['employee_id'] = creator_id
                        mandor_stats[creator_id]['employee_name'] = creator_name
                        mandor_stats[creator_id]['total_transactions'] += 1
                        mandor_stats[creator_id]['divisions'].add(division)
                        
                        # Hitung verifikasi (status 704)
                        if transstatus == '704':
                            mandor_stats[creator_id]['verified_transactions'] += 1
                        
                        mandor_stats[creator_id]['transaction_details'].append({
                            'transno': transno,
                            'transdate': transdate,
                            'transstatus': transstatus,
                            'division': division
                        })
                        
                except Exception as e:
                    continue
            
            # Tampilkan hasil analisis
            print(f"\nRESULT ANALISIS MANDOR:")
            print("="*60)
            
            total_mandor_transactions = 0
            total_mandor_verifications = 0
            
            for mandor_id, stats in mandor_stats.items():
                total_mandor_transactions += stats['total_transactions']
                total_mandor_verifications += stats['verified_transactions']
                
                verification_rate = (stats['verified_transactions'] / stats['total_transactions'] * 100) if stats['total_transactions'] > 0 else 0
                
                print(f"\nMANDOR: {stats['employee_name']} (ID: {mandor_id})")
                print(f"  - Total Transaksi: {stats['total_transactions']}")
                print(f"  - Verifikasi (Status 704): {stats['verified_transactions']}")
                print(f"  - Verification Rate: {verification_rate:.2f}%")
                print(f"  - Divisi: {', '.join(stats['divisions'])}")
                
                # Breakdown per divisi
                div_breakdown = defaultdict(lambda: {'total': 0, 'verified': 0})
                for detail in stats['transaction_details']:
                    div_breakdown[detail['division']]['total'] += 1
                    if detail['transstatus'] == '704':
                        div_breakdown[detail['division']]['verified'] += 1
                
                for div, counts in div_breakdown.items():
                    div_rate = (counts['verified'] / counts['total'] * 100) if counts['total'] > 0 else 0
                    print(f"    * {div}: {counts['verified']}/{counts['total']} ({div_rate:.2f}%)")
            
            print(f"\nSUMMARY KESELURUHAN:")
            print(f"Total MANDOR: {len(mandor_stats)}")
            print(f"Total Transaksi MANDOR: {total_mandor_transactions}")
            print(f"Total Verifikasi MANDOR: {total_mandor_verifications}")
            overall_rate = (total_mandor_verifications / total_mandor_transactions * 100) if total_mandor_transactions > 0 else 0
            print(f"Overall Verification Rate: {overall_rate:.2f}%")
            
            # Validasi khusus untuk SCANUSERID = '3613'
            print(f"\nVALIDASI KHUSUS SCANUSERID = '3613':")
            if '3613' in mandor_stats:
                stats_3613 = mandor_stats['3613']
                print(f"Nama: {stats_3613['employee_name']}")
                print(f"Total Transaksi: {stats_3613['total_transactions']}")
                print(f"Verifikasi: {stats_3613['verified_transactions']}")
                print(f"Divisi: {', '.join(stats_3613['divisions'])}")
                
                # Bandingkan dengan hasil crosscheck
                print(f"\nPERBANDINGAN DENGAN CROSSCHECK:")
                print(f"Crosscheck menunjukkan: 212 transaksi")
                print(f"Analisis ini menunjukkan: {stats_3613['total_transactions']} transaksi")
                
                if stats_3613['total_transactions'] == 212:
                    print("✅ HASIL KONSISTEN dengan crosscheck!")
                else:
                    print("❌ HASIL TIDAK KONSISTEN dengan crosscheck!")
            else:
                print("❌ SCANUSERID = '3613' tidak ditemukan dalam data P5")
        
        else:
            print("Tidak ada data MANDOR (P5) ditemukan")
            
    except Exception as e:
        print(f"Error saat menjalankan analisis: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("ANALISIS SELESAI")

if __name__ == "__main__":
    analyze_mandor_accurate() 