#!/usr/bin/env python3
"""
Debug script untuk memeriksa mengapa Erly masih 117 bukan 123
"""

from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def debug_erly():
    """Debug Erly transactions"""
    print("DEBUG ERLY TRANSACTIONS")
    print("="*50)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # Query 1: Exact query yang Anda berikan
        print("\n1. QUERY YANG ANDA BERIKAN:")
        query1 = """
        SELECT COUNT(*) as total
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        """
        
        result1 = connector.execute_query(query1)
        df1 = connector.to_pandas(result1)
        
        if not df1.empty:
            count1 = int(df1.iloc[0, 0])
            print(f"Result: {count1} transaksi")
            print(f"Expected: 123")
            print(f"Status: {'✓ MATCH' if count1 == 123 else '✗ MISMATCH'}")
        
        # Query 2: Cek dengan date range yang berbeda
        print("\n2. QUERY DENGAN DATE RANGE < 2025-04-30:")
        query2 = """
        SELECT COUNT(*) as total
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-30'
        """
        
        result2 = connector.execute_query(query2)
        df2 = connector.to_pandas(result2)
        
        if not df2.empty:
            count2 = int(df2.iloc[0, 0])
            print(f"Result: {count2} transaksi")
        
        # Query 3: Cek dengan date range <= 2025-04-28
        print("\n3. QUERY DENGAN DATE RANGE <= 2025-04-28:")
        query3 = """
        SELECT COUNT(*) as total
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE <= '2025-04-28'
        """
        
        result3 = connector.execute_query(query3)
        df3 = connector.to_pandas(result3)
        
        if not df3.empty:
            count3 = int(df3.iloc[0, 0])
            print(f"Result: {count3} transaksi")
        
        # Query 4: Cek detail transaksi per tanggal
        print("\n4. DETAIL TRANSAKSI PER TANGGAL:")
        query4 = """
        SELECT a.TRANSDATE, COUNT(*) as daily_count
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        GROUP BY a.TRANSDATE
        ORDER BY a.TRANSDATE
        """
        
        result4 = connector.execute_query(query4)
        df4 = connector.to_pandas(result4)
        
        if not df4.empty:
            total_from_details = 0
            for _, row in df4.iterrows():
                date = row.iloc[0]
                count = int(row.iloc[1])
                total_from_details += count
                print(f"  {date}: {count} transaksi")
            
            print(f"Total dari detail: {total_from_details}")
        
        # Query 5: Cek apakah ada data di tanggal 28 dan 29
        print("\n5. CEK DATA TANGGAL 28-29 APRIL:")
        query5 = """
        SELECT a.TRANSDATE, COUNT(*) as daily_count
        FROM FFBSCANNERDATA04 a 
        JOIN OCFIELD b ON a.FIELDID = b.ID 
        WHERE b.DIVID = '16' 
            AND a.RECORDTAG = 'PM' 
            AND a.SCANUSERID = '4771' 
            AND a.TRANSDATE IN ('2025-04-28', '2025-04-29')
        GROUP BY a.TRANSDATE
        ORDER BY a.TRANSDATE
        """
        
        result5 = connector.execute_query(query5)
        df5 = connector.to_pandas(result5)
        
        if not df5.empty:
            for _, row in df5.iterrows():
                date = row.iloc[0]
                count = int(row.iloc[1])
                print(f"  {date}: {count} transaksi")
        else:
            print("  Tidak ada data di tanggal 28-29 April")
        
        # Query 6: Cek query yang digunakan script analisis
        print("\n6. QUERY YANG DIGUNAKAN SCRIPT ANALISIS:")
        query6 = """
        SELECT
            a.ID,
            a.SCANUSERID,
            a.RECORDTAG,
            a.TRANSDATE
        FROM
            FFBSCANNERDATA04 a
        JOIN
            OCFIELD b ON a.FIELDID = b.ID
        WHERE
            b.DIVID = '16'
            AND a.SCANUSERID = '4771'
            AND a.RECORDTAG = 'PM'
            AND a.TRANSDATE >= '2025-04-01' 
            AND a.TRANSDATE < '2025-04-29'
        ORDER BY a.TRANSDATE
        """
        
        result6 = connector.execute_query(query6)
        df6 = connector.to_pandas(result6)
        
        print(f"Script query result: {len(df6)} transaksi")
        
        if not df6.empty:
            # Cek beberapa sample data
            print("Sample data:")
            for i in range(min(5, len(df6))):
                row = df6.iloc[i]
                print(f"  ID: {row.iloc[0]}, SCANUSERID: {row.iloc[1]}, RECORDTAG: {row.iloc[2]}, DATE: {row.iloc[3]}")
        
        print(f"\n" + "="*50)
        print("SUMMARY:")
        print(f"Query 1 (< 2025-04-29): {count1 if 'count1' in locals() else 'N/A'}")
        print(f"Query 2 (< 2025-04-30): {count2 if 'count2' in locals() else 'N/A'}")
        print(f"Query 3 (<= 2025-04-28): {count3 if 'count3' in locals() else 'N/A'}")
        print(f"Script query: {len(df6) if not df6.empty else 'N/A'}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_erly()
