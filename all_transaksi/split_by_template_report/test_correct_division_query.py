#!/usr/bin/env python3
"""
Test the correct division query using proper table relationships
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
    print("Testing Correct Division Query")
    print("=" * 60)
    
    # Test 1: Check the relationship between FFBSCANNERDATA04 and OCFIELD
    run_isql_query(
        """SELECT FIRST 10 
               f.FIELDID, 
               o.ID as OCFIELD_ID, 
               o.DIVID, 
               o.RYSDIVCODE
           FROM FFBSCANNERDATA04 f 
           LEFT JOIN OCFIELD o ON f.FIELDID = o.ID 
           ORDER BY f.ID""",
        "1. Test join: FFBSCANNERDATA04.FIELDID = OCFIELD.ID"
    )
    
    # Test 2: Check the relationship between OCFIELD and CRDIVISION using RYSDIVCODE
    run_isql_query(
        """SELECT FIRST 10 
               o.ID, 
               o.RYSDIVCODE, 
               d.DIVCODE, 
               d.DIVNAME
           FROM OCFIELD o 
           LEFT JOIN CRDIVISION d ON o.RYSDIVCODE = d.DIVCODE 
           ORDER BY o.ID""",
        "2. Test join: OCFIELD.RYSDIVCODE = CRDIVISION.DIVCODE"
    )
    
    # Test 3: Full corrected division query
    run_isql_query(
        """SELECT DISTINCT 
               f.FIELDID, 
               o.RYSDIVCODE as DIVCODE, 
               d.DIVNAME
           FROM FFBSCANNERDATA04 f 
           LEFT JOIN OCFIELD o ON f.FIELDID = o.ID 
           LEFT JOIN CRDIVISION d ON o.RYSDIVCODE = d.DIVCODE 
           WHERE d.DIVNAME IS NOT NULL
           ORDER BY f.FIELDID""",
        "3. Corrected division query"
    )
    
    # Test 4: Count successful joins
    run_isql_query(
        """SELECT 
               COUNT(*) as TOTAL_RECORDS,
               COUNT(d.DIVNAME) as RECORDS_WITH_DIVISION
           FROM FFBSCANNERDATA04 f 
           LEFT JOIN OCFIELD o ON f.FIELDID = o.ID 
           LEFT JOIN CRDIVISION d ON o.RYSDIVCODE = d.DIVCODE""",
        "4. Count of records with successful division mapping"
    )
    
    # Test 5: Alternative - try using DIVID from OCFIELD
    run_isql_query(
        """SELECT FIRST 10 
               o.DIVID, 
               d.ID as CRDIV_ID, 
               d.DIVNAME
           FROM OCFIELD o 
           LEFT JOIN CRDIVISION d ON o.DIVID = d.ID 
           ORDER BY o.ID""",
        "5. Alternative: OCFIELD.DIVID = CRDIVISION.ID"
    )
    
    # Test 6: Full alternative division query using DIVID
    run_isql_query(
        """SELECT DISTINCT 
               f.FIELDID, 
               o.DIVID, 
               d.DIVNAME, 
               d.DIVCODE
           FROM FFBSCANNERDATA04 f 
           LEFT JOIN OCFIELD o ON f.FIELDID = o.ID 
           LEFT JOIN CRDIVISION d ON o.DIVID = d.ID 
           WHERE d.DIVNAME IS NOT NULL
           ORDER BY f.FIELDID""",
        "6. Alternative division query using DIVID"
    )

if __name__ == "__main__":
    main()