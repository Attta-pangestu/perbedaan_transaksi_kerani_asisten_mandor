#!/usr/bin/env python3
"""
Test direct isql connection to debug the issue
"""

import subprocess
import tempfile
import os

def test_direct_isql():
    """Test direct isql connection"""
    try:
        print("=== Testing Direct ISQL Connection ===")
        
        # Check if database file exists
        db_path = 'D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB'
        print(f"Database file exists: {os.path.exists(db_path)}")
        
        # Test with localhost connection
        isql_path = 'C:\\Program Files (x86)\\Firebird\\Firebird_1_5\\bin\\isql.exe'
        
        # Create SQL file with CONNECT statement
        sql_content = """CONNECT localhost:'D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB' USER 'SYSDBA' PASSWORD 'masterkey';
SELECT 1 FROM RDB$DATABASE;
EXIT;
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write(sql_content)
            temp_sql_path = temp_file.name
        
        print(f"SQL file created: {temp_sql_path}")
        print(f"SQL content:\n{sql_content}")
        
        # Execute isql command
        cmd = [isql_path, '-input', temp_sql_path]
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
        # Test without localhost
        print("\n=== Testing Without Localhost ===")
        sql_content2 = """CONNECT 'D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB' USER 'SYSDBA' PASSWORD 'masterkey';
SELECT 1 FROM RDB$DATABASE;
EXIT;
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file2:
            temp_file2.write(sql_content2)
            temp_sql_path2 = temp_file2.name
        
        print(f"SQL content:\n{sql_content2}")
        
        cmd2 = [isql_path, '-input', temp_sql_path2]
        result2 = subprocess.run(cmd2, capture_output=True, text=True, 
                               creationflags=subprocess.CREATE_NO_WINDOW)
        
        print(f"Return code: {result2.returncode}")
        print(f"STDOUT:\n{result2.stdout}")
        print(f"STDERR:\n{result2.stderr}")
        
        # Cleanup
        try:
            os.unlink(temp_sql_path)
            os.unlink(temp_sql_path2)
        except:
            pass
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_isql()