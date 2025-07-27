#!/usr/bin/env python3
"""
Script untuk crosscheck jumlah transaksi MANDOR dengan SCANUSERID = '3613'
sesuai dengan query yang diberikan user.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'all_transaksi'))

from firebird_connector import FirebirdConnector

def crosscheck_mandor_transactions():
    """
    Crosscheck jumlah transaksi MANDOR dengan SCANUSERID = '3613' untuk bulan 05/2025
    """
    # Konfigurasi database
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    
    print("CROSSCHECK TRANSAKSI MANDOR SCANUSERID = '3613'")
    print("="*60)
    
    # Setup database connection
    print("Menghubungkan ke database...")
    connector = FirebirdConnector(DB_PATH)
    
    if not connector.test_connection():
        print("Koneksi database gagal!")
        return
    
    print("Koneksi database berhasil")
    
    # Query sesuai yang diberikan user
    query = """
    SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO, 
           a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH, 
           a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME, 
           a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED, 
           a.UNDERRIPEBCH, a.OVERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
    FROM FFBSCANNERDATA05 a
    WHERE a.SCANUSERID = '3613'  
    AND a.TRANSDATE >= '2025-05-01' 
    AND a.TRANSDATE < '2025-06-01'
    """
    
    print("\nMenjalankan query crosscheck...")
    print("Query:")
    print(query)
    print("\n" + "="*60)
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df is not None and not df.empty:
            print(f"HASIL CROSSCHECK:")
            print(f"Total transaksi MANDOR dengan SCANUSERID = '3613': {len(df)}")
            print(f"Periode: 2025-05-01 sampai 2025-06-01")
            
            # Analisis lebih detail
            print(f"\nDETAIL ANALISIS:")
            
            # Cek kolom RECORDTAG
            if 'RECORDTAG' in df.columns:
                recordtag_counts = df['RECORDTAG'].value_counts()
                print(f"Breakdown berdasarkan RECORDTAG:")
                for recordtag, count in recordtag_counts.items():
                    print(f"  - {recordtag}: {count} transaksi")
            
            # Cek kolom TRANSSTATUS
            if 'TRANSSTATUS' in df.columns:
                status_counts = df['TRANSSTATUS'].value_counts()
                print(f"\nBreakdown berdasarkan TRANSSTATUS:")
                for status, count in status_counts.items():
                    print(f"  - Status {status}: {count} transaksi")
            
            # Cek tanggal
            if 'TRANSDATE' in df.columns:
                date_counts = df['TRANSDATE'].value_counts().sort_index()
                print(f"\nBreakdown berdasarkan tanggal (5 pertama):")
                for date, count in date_counts.head().items():
                    print(f"  - {date}: {count} transaksi")
                if len(date_counts) > 5:
                    print(f"  ... dan {len(date_counts)-5} tanggal lainnya")
            
            # Tampilkan beberapa sample data
            print(f"\nSample data (5 baris pertama):")
            sample_cols = ['TRANSNO', 'TRANSDATE', 'RECORDTAG', 'TRANSSTATUS']
            available_cols = [col for col in sample_cols if col in df.columns]
            if available_cols:
                print(df[available_cols].head().to_string(index=False))
            
        else:
            print("HASIL: Tidak ada data yang ditemukan untuk SCANUSERID = '3613'")
            
    except Exception as e:
        print(f"Error saat menjalankan query: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("CROSSCHECK SELESAI")

if __name__ == "__main__":
    crosscheck_mandor_transactions() 