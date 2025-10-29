#!/usr/bin/env python3
"""
Test division query using localhost connection method
"""

import subprocess
import tempfile
import os

def run_isql_query(sql_query, description):
    """Run an ISQL query and return the results"""
    print(f"\n{description}")
    print("=" * 50)
    
    # Create temporary SQL file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(f"CONNECT localhost:D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB USER 'SYSDBA' PASSWORD 'masterkey';\n")
        f.write(sql_query + ";\n")
        f.write("EXIT;\n")
        temp_file = f.name
    
    try:
        # Run isql command
        isql_path = r"C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe"
        result = subprocess.run(
            [isql_path, "-i", temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.stdout, result.stderr, result.returncode
        
    except Exception as e:
        print(f"Error running query: {e}")
        return "", str(e), -1
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass

def main():
    print("Testing Division Queries with Localhost Connection")
    print("=" * 60)
    
    # Test 1: Check CRDIVISION table structure
    run_isql_query(
        "SELECT FIRST 5 * FROM CRDIVISION",
        "1. Sample data from CRDIVISION table"
    )
    
    # Test 2: Check FFBSCANNERDATA04 table structure
    run_isql_query(
        "SELECT FIRST 5 * FROM FFBSCANNERDATA04",
        "2. Sample data from FFBSCANNERDATA04 table"
    )
    
    # Test 3: Check OCFIELD table structure
    run_isql_query(
        "SELECT FIRST 5 * FROM OCFIELD",
        "3. Sample data from OCFIELD table"
    )
    
    # Test 4: Original division query from get_division_list
    division_query = """
    SELECT DISTINCT 
        f.DIVID, 
        d.DIVNAME, 
        d.DIVCODE 
    FROM FFBSCANNERDATA04 f 
    LEFT JOIN OCFIELD o ON f.DIVID = o.DIVID 
    LEFT JOIN CRDIVISION d ON o.DIVCODE = d.DIVCODE 
    ORDER BY f.DIVID
    """
    run_isql_query(division_query, "4. Original division query from get_division_list")
    
    # Test 5: Check what columns actually exist in each table
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'CRDIVISION'""",
        "5. Columns in CRDIVISION table"
    )
    
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'FFBSCANNERDATA04'""",
        "6. Columns in FFBSCANNERDATA04 table"
    )
    
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'OCFIELD'""",
        "7. Columns in OCFIELD table"
    )
    
    # Test 6: Count records in each table
    run_isql_query("SELECT COUNT(*) as CRDIVISION_COUNT FROM CRDIVISION", "8. Record count in CRDIVISION")
    run_isql_query("SELECT COUNT(*) as FFBSCANNERDATA04_COUNT FROM FFBSCANNERDATA04", "9. Record count in FFBSCANNERDATA04")
    run_isql_query("SELECT COUNT(*) as OCFIELD_COUNT FROM OCFIELD", "10. Record count in OCFIELD")

if __name__ == "__main__":
    main()