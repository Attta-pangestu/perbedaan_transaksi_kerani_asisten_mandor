#!/usr/bin/env python3
"""
Simple division query test without TRIM function for Firebird 1.5 compatibility
"""

from core.database_connector import DatabaseConnectorFactory

def test_simple_division_query():
    """Test with simple queries without TRIM function"""
    try:
        print("=== Testing Simple Division Query ===")
        
        # Create connector
        connector = DatabaseConnectorFactory.create_connector('firebird', 
            db_path='D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB',
            username='SYSDBA', 
            password='masterkey')
        
        if not connector.test_connection():
            print("✗ Database connection failed")
            return
            
        print("✓ Database connection successful\n")
        
        # Test simple division query without TRIM
        print("=== Testing Simple Division Query ===")
        division_query = """
        SELECT DISTINCT o.DIVID as DIVISION_ID, 
               c.ID as CRDIV_ID,
               c."LENTOCRMK MRDIVRMK LASTUSER" as DIVISION_NAME
        FROM OCFIELD o 
        JOIN CRDIVISION c ON o.DIVID = c.ID
        WHERE o.DIVID IS NOT NULL AND c.ID IS NOT NULL
        ORDER BY c."LENTOCRMK MRDIVRMK LASTUSER"
        """
        
        result = connector.execute_query(division_query)
        if result:
            print(f"Division query returned {len(result)} divisions:")
            for row in result:
                print(f"  ID: {row.get('DIVISION_ID')}, Name: '{row.get('DIVISION_NAME')}'")
        else:
            print("No results returned")
            
        # Test the full mapping without TRIM
        print("\n=== Testing Full Division Mapping ===")
        full_query = """
        SELECT FIRST 10 f.FIELDID, 
               o.ID as OCFIELD_ID, 
               o.DIVID,
               c.ID as CRDIV_ID,
               c."LENTOCRMK MRDIVRMK LASTUSER" as DIVISION_NAME
        FROM FFBSCANNERDATA04 f
        JOIN OCFIELD o ON f.FIELDID = o.ID
        JOIN CRDIVISION c ON o.DIVID = c.ID
        WHERE o.DIVID IS NOT NULL AND c.ID IS NOT NULL
        """
        
        result = connector.execute_query(full_query)
        if result:
            print(f"Full mapping query returned {len(result)} rows:")
            for row in result:
                print(f"  FIELDID: {row.get('FIELDID')}, DIVID: {row.get('DIVID')}, DIVISION_NAME: '{row.get('DIVISION_NAME')}'")
        else:
            print("No results returned for full mapping")
            
        # Test raw CRDIVISION data to understand structure
        print("\n=== Raw CRDIVISION Data ===")
        raw_query = "SELECT FIRST 5 * FROM CRDIVISION WHERE ID IS NOT NULL"
        
        result = connector.execute_query(raw_query)
        if result:
            print("Raw CRDIVISION data:")
            for i, row in enumerate(result):
                print(f"  Row {i+1}:")
                for key, value in row.items():
                    print(f"    '{key}': '{value}'")
                print()
                
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_division_query()