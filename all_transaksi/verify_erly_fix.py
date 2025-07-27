#!/usr/bin/env python3
"""
Verifikasi sederhana untuk memastikan query Erly menghasilkan 123 transaksi
"""

from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def main():
    print("VERIFIKASI QUERY ERLY")
    print("="*30)
    
    connector = FirebirdConnector(DB_PATH)
    
    # Test connection
    if not connector.test_connection():
        print("Database connection failed!")
        return
    
    print("Database connected successfully")
    
    # Query yang diberikan user
    query = """
    SELECT COUNT(*) as total
    FROM FFBSCANNERDATA04 a 
    JOIN OCFIELD b ON a.FIELDID = b.ID 
    WHERE b.DIVID = '16' 
        AND a.RECORDTAG = 'PM' 
        AND a.SCANUSERID = '4771' 
        AND a.TRANSDATE >= '2025-04-01' 
        AND a.TRANSDATE < '2025-04-29'
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if not df.empty:
            total = int(df.iloc[0, 0])
            print(f"Erly (SCANUSERID 4771) transactions: {total}")
            print(f"Expected: 123")
            print(f"Status: {'✓ MATCH' if total == 123 else '✗ MISMATCH'}")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
