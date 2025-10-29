#!/usr/bin/env python3
"""
Test script to verify the updated database connector with localhost connection
"""

from core.database_connector import DatabaseConnectorFactory

def test_updated_connector():
    """Test the updated database connector"""
    try:
        print("=== Testing Updated Database Connector ===")
        
        # Create connector with localhost connection (now default)
        connector = DatabaseConnectorFactory.create_connector('firebird', 
            db_path='D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB',
            username='SYSDBA', 
            password='masterkey')
        
        # Test connection
        print("Testing connection...")
        if connector.test_connection():
            print("✓ Database connection successful")
            
            print("\n=== Testing Division Query ===")
            divisions = connector.get_division_list()
            print(f"Found {len(divisions)} divisions:")
            for div in divisions[:10]:  # Show first 10 divisions
                print(f"- ID: {div['div_id']}, Name: {div['div_name']}")
            
            print("\n=== Testing Table Count ===")
            tables = connector.get_tables()
            print(f"Found {len(tables)} tables")
            
            print("\n=== Testing Sample Query ===")
            sample_query = "SELECT FIRST 5 FIELDID, ID FROM OCFIELD WHERE DIVID IS NOT NULL"
            result = connector.execute_query(sample_query)
            if result:
                print(f"Sample query returned {len(result)} rows:")
                for row in result:
                    print(f"  FIELDID: {row.get('FIELDID')}, ID: {row.get('ID')}")
            else:
                print("Sample query returned no data")
                
        else:
            print("✗ Database connection failed")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_connector()