#!/usr/bin/env python3
"""
Test script to verify database connection and division mapping
"""

from core.database_connector import DatabaseConnectorFactory

def test_database_connection():
    """Test database connection and division mapping"""
    try:
        print("=== Testing Database Connection ===")
        
        # Create connector
        connector = DatabaseConnectorFactory.create_connector('firebird', 
            db_path='D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB',
            username='SYSDBA', 
            password='masterkey')
        
        # Test connection
        if connector.test_connection():
            print("✓ Database connection successful")
            
            print("\n=== Available Tables ===")
            tables = connector.get_tables()
            print(f"Found {len(tables)} tables:")
            for table in sorted(tables)[:20]:  # Show first 20 tables
                print(f"- {table}")
            
            print("\n=== Testing Division Query ===")
            result = connector.get_division_list()
            print(f"Found {len(result)} divisions:")
            for div in result[:10]:  # Show first 10 divisions
                print(f"- ID: {div['div_id']}, Name: {div['div_name']}")
            
            # Test specific queries to understand table structure
            print("\n=== Testing Table Structure ===")
            
            # Check if TRANSAKSI_FFB table exists (from template config)
            test_queries = [
                "SELECT FIRST 1 * FROM FFBSCANNERDATA04",
                "SELECT FIRST 1 * FROM OCFIELD", 
                "SELECT FIRST 1 * FROM CRDIVISION"
            ]
            
            for query in test_queries:
                try:
                    result = connector.execute_query(query)
                    if result:
                        print(f"✓ Query successful: {query}")
                        if len(result) > 0:
                            print(f"  Sample columns: {list(result[0].keys())}")
                    else:
                        print(f"✗ Query returned no data: {query}")
                except Exception as e:
                    print(f"✗ Query failed: {query} - {str(e)}")
            
            # Test the template's division query
            print("\n=== Testing Template Division Query ===")
            template_query = "SELECT DISTINCT DIVISI FROM TRANSAKSI_FFB ORDER BY DIVISI"
            try:
                result = connector.execute_query(template_query)
                if result:
                    print(f"✓ Template division query successful, found {len(result)} divisions")
                    for row in result[:5]:
                        print(f"  - {row}")
                else:
                    print("✗ Template division query returned no data")
            except Exception as e:
                print(f"✗ Template division query failed: {str(e)}")
                print("  This indicates the TRANSAKSI_FFB table may not exist or have different structure")
        
        else:
            print("✗ Database connection failed")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()