#!/usr/bin/env python3
"""
Test simple query untuk Erly
"""

from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def test_simple():
    """Test simple query"""
    print("SIMPLE TEST - ERLY QUERY")
    print("="*30)
    
    connector = FirebirdConnector(DB_PATH)
    
    if not connector.test_connection():
        print("Connection failed!")
        return
    
    print("Connected!")
    
    # Query persis seperti yang user berikan
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
            count = int(df.iloc[0, 0])
            print(f"Erly transactions: {count}")
            print(f"Expected: 123")
            print(f"Match: {'YES' if count == 123 else 'NO'}")
            
            if count != 123:
                print(f"Difference: {count - 123}")
        else:
            print("No results!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()
