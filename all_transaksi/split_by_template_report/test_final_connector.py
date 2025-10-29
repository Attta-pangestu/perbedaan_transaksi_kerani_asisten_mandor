#!/usr/bin/env python3
"""
Final test of the updated database connector with correct queries
"""

from core.database_connector import DatabaseConnectorFactory

def test_final_connector():
    """Test the final updated database connector"""
    try:
        print("=== Testing Final Database Connector ===")
        
        # Create connector with TCP connection
        connector = DatabaseConnectorFactory.create_connector('firebird', 
            db_path='D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB',
            username='SYSDBA', 
            password='masterkey')
        
        # Test connection
        print("Testing connection...")
        if connector.test_connection():
            print("✓ Database connection successful")
            
            print("\n=== Testing Simple Query ===")
            simple_query = "SELECT 1 AS TEST FROM RDB$DATABASE"
            result = connector.execute_query(simple_query)
            if result:
                print(f"Simple query successful: {result}")
            
            print("\n=== Testing OCFIELD Query ===")
            ocfield_query = "SELECT FIRST 5 ID, DIVID FROM OCFIELD WHERE DIVID IS NOT NULL"
            result = connector.execute_query(ocfield_query)
            if result:
                print(f"OCFIELD query returned {len(result)} rows:")
                for row in result:
                    print(f"  ID: {row.get('ID')}, DIVID: {row.get('DIVID')}")
            
            print("\n=== Testing Division Query ===")
            division_query = """
            SELECT DISTINCT o.DIVID, c.DIVNAME 
            FROM OCFIELD o 
            JOIN CRDIVISION c ON o.DIVID = c.ID 
            WHERE o.DIVID IS NOT NULL
            ORDER BY c.DIVNAME
            """
            result = connector.execute_query(division_query)
            if result:
                print(f"Division query returned {len(result)} divisions:")
                for row in result[:10]:  # Show first 10
                    print(f"  ID: {row.get('DIVID')}, Name: {row.get('DIVNAME')}")
            
            print("\n=== Testing Full Division Mapping ===")
            full_query = """
            SELECT FIRST 10 f.FIELDID, o.ID as OCFIELD_ID, o.DIVID, c.DIVNAME
            FROM FFBSCANNERDATA04 f
            JOIN OCFIELD o ON f.FIELDID = o.ID
            JOIN CRDIVISION c ON o.DIVID = c.ID
            WHERE o.DIVID IS NOT NULL
            """
            result = connector.execute_query(full_query)
            if result:
                print(f"Full mapping query returned {len(result)} rows:")
                for row in result:
                    print(f"  FIELDID: {row.get('FIELDID')}, DIVID: {row.get('DIVID')}, DIVNAME: {row.get('DIVNAME')}")
                    
        else:
            print("✗ Database connection failed")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_connector()