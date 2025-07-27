#!/usr/bin/env python3
"""
Script untuk crosscheck dengan query yang sama seperti sistem analisis MANDOR
(dengan JOIN divisi) untuk membandingkan hasil.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'all_transaksi'))

from firebird_connector import FirebirdConnector

def crosscheck_mandor_with_join():
    """
    Crosscheck dengan query yang sama seperti sistem analisis MANDOR
    """
    # Konfigurasi database
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    
    print("CROSSCHECK DENGAN QUERY SISTEM ANALISIS MANDOR")
    print("="*60)
    
    # Setup database connection
    print("Menghubungkan ke database...")
    connector = FirebirdConnector(DB_PATH)
    
    if not connector.test_connection():
        print("Koneksi database gagal!")
        return
    
    print("Koneksi database berhasil")
    
    # Query yang sama dengan sistem analisis MANDOR (dengan JOIN)
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
    AND a.SCANUSERID = '3613'
    ORDER BY c.DIVNAME, a.TRANSNO, a.TRANSDATE, a.TRANSTIME
    """
    
    print("\nMenjalankan query dengan JOIN (seperti sistem analisis)...")
    print("Query:")
    print(query)
    print("\n" + "="*60)
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df is not None and not df.empty:
            print(f"HASIL CROSSCHECK DENGAN JOIN:")
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
            
            # Cek kolom DIVNAME
            if 'DIVNAME' in df.columns:
                divname_counts = df['DIVNAME'].value_counts()
                print(f"\nBreakdown berdasarkan DIVNAME:")
                for divname, count in divname_counts.items():
                    print(f"  - {divname}: {count} transaksi")
            
            # Cek NULL values di DIVNAME
            null_divname = df['DIVNAME'].isnull().sum()
            print(f"\nTransaksi dengan DIVNAME NULL: {null_divname}")
            
            # Tampilkan beberapa sample data
            print(f"\nSample data (5 baris pertama):")
            sample_cols = ['TRANSNO', 'TRANSDATE', 'RECORDTAG', 'TRANSSTATUS', 'DIVNAME']
            available_cols = [col for col in sample_cols if col in df.columns]
            if available_cols:
                print(df[available_cols].head().to_string(index=False))
            
        else:
            print("HASIL: Tidak ada data yang ditemukan dengan query JOIN")
            
    except Exception as e:
        print(f"Error saat menjalankan query: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    
    # Sekarang bandingkan dengan query tanpa JOIN
    print("MEMBANDINGKAN DENGAN QUERY TANPA JOIN...")
    
    query_no_join = """
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
    
    try:
        result_no_join = connector.execute_query(query_no_join)
        df_no_join = connector.to_pandas(result_no_join)
        
        if df_no_join is not None and not df_no_join.empty:
            print(f"HASIL QUERY TANPA JOIN:")
            print(f"Total transaksi: {len(df_no_join)}")
            
            print(f"\nPERBANDINGAN:")
            print(f"Query dengan JOIN: {len(df) if df is not None and not df.empty else 0} transaksi")
            print(f"Query tanpa JOIN: {len(df_no_join)} transaksi")
            
            if df is not None and not df.empty:
                selisih = len(df_no_join) - len(df)
                print(f"Selisih: {selisih} transaksi hilang karena JOIN")
                
                if selisih > 0:
                    print(f"\n⚠️  MASALAH TERIDENTIFIKASI:")
                    print(f"Ada {selisih} transaksi yang hilang karena LEFT JOIN dengan tabel divisi")
                    print(f"Kemungkinan beberapa FIELDID tidak memiliki mapping di OCFIELD/CRDIVISION")
        
    except Exception as e:
        print(f"Error saat menjalankan query tanpa JOIN: {e}")
    
    print("\n" + "="*60)
    print("CROSSCHECK SELESAI")

if __name__ == "__main__":
    crosscheck_mandor_with_join() 