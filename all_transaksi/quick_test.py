#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from firebird_connector import FirebirdConnector

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def quick_test():
    print("QUICK TEST")
    print("="*20)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if connector.test_connection():
            print("Connected!")
            
            # Test exact query
            query = """
            SELECT COUNT(*) 
            FROM FFBSCANNERDATA04 a 
            JOIN OCFIELD b ON a.FIELDID = b.ID 
            WHERE b.DIVID = '16' 
                AND a.RECORDTAG = 'PM' 
                AND a.SCANUSERID = '4771' 
                AND a.TRANSDATE >= '2025-04-01' 
                AND a.TRANSDATE < '2025-04-29'
            """
            
            result = connector.execute_query(query)
            df = connector.to_pandas(result)
            
            if not df.empty:
                count = int(df.iloc[0, 0])
                print(f"Erly count: {count}")
                print(f"Expected: 123")
                print(f"Match: {'YES' if count == 123 else 'NO'}")
            else:
                print("No data")
        else:
            print("Connection failed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()
