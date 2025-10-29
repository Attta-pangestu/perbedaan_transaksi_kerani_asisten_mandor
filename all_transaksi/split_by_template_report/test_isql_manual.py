#!/usr/bin/env python3
"""
Script to test isql with the exact command format used by the connector
"""

import subprocess
import os
import tempfile

def test_isql_manual():
    """Test isql with exact connector format"""
    try:
        print("=== Testing ISQL with Connector Format ===")
        
        db_path = 'D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB'
        username = 'SYSDBA'
        password = 'masterkey'
        isql_path = r'C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe'
        
        # Test 1: Simple query using connector format
        print("\n1. Testing simple query with connector format:")
        
        # Create temporary SQL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write("SELECT 'Connection Test' AS TEST FROM RDB$DATABASE;\n")
            temp_file.write("EXIT;\n")
            temp_sql_path = temp_file.name
        
        try:
            # Use exact command format from connector
            cmd = [
                isql_path,
                '-user', username,
                '-password', password,
                '-input', temp_sql_path,
                db_path  # Database path as last argument
            ]
            
            print(f"Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                os.unlink(temp_sql_path)
            except:
                pass
        
        # Test 2: Table count query
        print("\n2. Testing table count query:")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write("SELECT COUNT(*) AS TABLE_COUNT FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0;\n")
            temp_file.write("EXIT;\n")
            temp_sql_path = temp_file.name
        
        try:
            cmd = [
                isql_path,
                '-user', username,
                '-password', password,
                '-input', temp_sql_path,
                db_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                os.unlink(temp_sql_path)
            except:
                pass
        
        # Test 3: List tables
        print("\n3. Testing table list:")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write("SELECT FIRST 10 RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 ORDER BY RDB$RELATION_NAME;\n")
            temp_file.write("EXIT;\n")
            temp_sql_path = temp_file.name
        
        try:
            cmd = [
                isql_path,
                '-user', username,
                '-password', password,
                '-input', temp_sql_path,
                db_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                os.unlink(temp_sql_path)
            except:
                pass
        
        # Test 4: Test division query from connector
        print("\n4. Testing division query from connector:")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write("""
            SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
            FROM FFBSCANNERDATA04 a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID IS NOT NULL
            ORDER BY c.DIVNAME;
            """)
            temp_file.write("EXIT;\n")
            temp_sql_path = temp_file.name
        
        try:
            cmd = [
                isql_path,
                '-user', username,
                '-password', password,
                '-input', temp_sql_path,
                db_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                os.unlink(temp_sql_path)
            except:
                pass
                
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_isql_manual()