#!/usr/bin/env python3
"""
Check actual column names in the database tables
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
        f.write("CONNECT 'localhost:D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\IFESS_2B_24-10-2025\\PTRJ_P2B.FDB' USER 'SYSDBA' PASSWORD 'masterkey';\n")
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
    print("Checking Actual Column Names in Database Tables")
    print("=" * 60)
    
    # Check FFBSCANNERDATA04 columns that might relate to division
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'FFBSCANNERDATA04' 
           AND UPPER(r.RDB$FIELD_NAME) LIKE '%DIV%'
           ORDER BY r.RDB$FIELD_NAME""",
        "1. FFBSCANNERDATA04 columns containing 'DIV'"
    )
    
    # Check OCFIELD columns that might relate to division
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'OCFIELD' 
           AND UPPER(r.RDB$FIELD_NAME) LIKE '%DIV%'
           ORDER BY r.RDB$FIELD_NAME""",
        "2. OCFIELD columns containing 'DIV'"
    )
    
    # Check CRDIVISION columns
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'CRDIVISION'
           ORDER BY r.RDB$FIELD_NAME""",
        "3. All CRDIVISION columns"
    )
    
    # Check first few records of FFBSCANNERDATA04 to see actual data
    run_isql_query(
        "SELECT FIRST 3 * FROM FFBSCANNERDATA04",
        "4. Sample FFBSCANNERDATA04 records"
    )
    
    # Check first few records of OCFIELD to see actual data
    run_isql_query(
        "SELECT FIRST 5 * FROM OCFIELD",
        "5. Sample OCFIELD records"
    )
    
    # Look for any field that might contain division information in FFBSCANNERDATA04
    run_isql_query(
        """SELECT r.RDB$FIELD_NAME 
           FROM RDB$RELATION_FIELDS r 
           WHERE r.RDB$RELATION_NAME = 'FFBSCANNERDATA04' 
           AND (UPPER(r.RDB$FIELD_NAME) LIKE '%FIELD%' 
                OR UPPER(r.RDB$FIELD_NAME) LIKE '%AREA%'
                OR UPPER(r.RDB$FIELD_NAME) LIKE '%BLOCK%'
                OR UPPER(r.RDB$FIELD_NAME) LIKE '%SECTION%')
           ORDER BY r.RDB$FIELD_NAME""",
        "6. FFBSCANNERDATA04 columns that might relate to field/area/division"
    )

if __name__ == "__main__":
    main()