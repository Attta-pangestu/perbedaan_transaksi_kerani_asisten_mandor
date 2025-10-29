#!/usr/bin/env python3
"""
Script to debug isql path and test database connectivity
"""

from core.database_connector import DatabaseConnectorFactory
import os
import subprocess

def debug_isql_path():
    """Debug isql path detection"""
    try:
        print("=== Debugging ISQL Path ===")
        
        # Test default paths
        default_paths = [
            r'C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe',
            r'C:\Program Files (x86)\Firebird-1.5.6.5026-0_win32_Manual\bin\isql.exe',
            r'C:\Program Files (x86)\Firebird\bin\isql.exe',
            r'C:\Program Files\Firebird\Firebird_2_5\bin\isql.exe',
            r'C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe',
            r'C:\Program Files\Firebird\bin\isql.exe'
        ]
        
        print("Checking default paths:")
        for path in default_paths:
            exists = os.path.exists(path)
            print(f"  {path}: {'✓' if exists else '✗'}")
        
        # Try to find isql in PATH
        print("\nChecking PATH:")
        try:
            result = subprocess.run(['where', 'isql.exe'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"  Found in PATH: {result.stdout.strip()}")
            else:
                print("  Not found in PATH")
        except Exception as e:
            print(f"  Error checking PATH: {e}")
        
        # Try to create connector and see what happens
        print("\n=== Testing Connector Creation ===")
        try:
            db_path = 'D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB'
            username = 'SYSDBA'
            password = 'masterkey'
            
            connector = DatabaseConnectorFactory.create_connector('firebird', 
                db_path=db_path,
                username=username, 
                password=password)
            
            print("✓ Connector created successfully")
            print(f"  ISQL Path: {connector.isql_path}")
            
            # Test connection
            if connector.test_connection():
                print("✓ Database connection successful")
                
                # Try to get tables
                tables = connector.get_tables()
                print(f"✓ Found {len(tables)} tables")
                if tables:
                    print("  First 10 tables:")
                    for table in tables[:10]:
                        print(f"    - {table}")
                
                # Try to get divisions
                divisions = connector.get_division_list()
                print(f"✓ Found {len(divisions)} divisions")
                if divisions:
                    print("  Divisions:")
                    for div in divisions[:5]:
                        print(f"    - {div}")
                        
            else:
                print("✗ Database connection failed")
                
        except FileNotFoundError as e:
            print(f"✗ ISQL not found: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_isql_path()