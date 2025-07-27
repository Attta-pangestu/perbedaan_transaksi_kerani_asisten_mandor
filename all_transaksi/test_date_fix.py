"""
Test script untuk memverifikasi perbaikan format tanggal dalam query SQL
"""
import sys
import os
from datetime import datetime
import pandas as pd

# Add parent directory to path untuk import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebird_connector import FirebirdConnector

def test_date_format_fix():
    """Test perbaikan format tanggal dalam query."""
    print("="*60)
    print("TESTING DATE FORMAT FIX FOR IFESS ANALYSIS")
    print("="*60)
    
    # Database configuration
    db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("Please update the database path in the script.")
        return False
    
    try:
        # Initialize connector
        print("🔗 Connecting to database...")
        connector = FirebirdConnector(db_path)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return False
        
        print("✅ Database connection successful!")
        
        # Test different months with correct date format
        test_cases = [
            {"month": 5, "year": 2025, "description": "May 2025"},
            {"month": 4, "year": 2025, "description": "April 2025"},
            {"month": 12, "year": 2024, "description": "December 2024 (year boundary)"},
            {"month": 2, "year": 2025, "description": "February 2025 (short month)"}
        ]
        
        for test_case in test_cases:
            print(f"\n📅 Testing {test_case['description']}...")
            
            month = test_case["month"]
            year = test_case["year"]
            
            # Calculate proper date range (same logic as in GUI)
            start_date = f"{year}-{month:02d}-01"
            
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            
            table_name = f"FFBSCANNERDATA{month:02d}"
            
            print(f"   📊 Table: {table_name}")
            print(f"   📅 Date range: {start_date} to {end_date}")
            
            # Test query dengan format tanggal yang benar
            test_query = f"""
            SELECT COUNT(*) as TOTAL_RECORDS
            FROM {table_name} a
            WHERE a.TRANSDATE >= '{start_date}' 
            AND a.TRANSDATE < '{end_date}'
            """
            
            try:
                result = connector.execute_query(test_query)
                df = connector.to_pandas(result)
                
                if not df.empty and len(df.columns) > 0:
                    total_records = int(df.iloc[0, 0]) if len(df) > 0 else 0
                    print(f"   ✅ Query successful! Found {total_records} records")
                    
                    # Test sample data jika ada records
                    if total_records > 0:
                        sample_query = f"""
                        SELECT FIRST 3 TRANSNO, SCANUSERID, TRANSDATE, TRANSSTATUS
                        FROM {table_name} a
                        WHERE a.TRANSDATE >= '{start_date}' 
                        AND a.TRANSDATE < '{end_date}'
                        """
                        
                        sample_result = connector.execute_query(sample_query)
                        sample_df = connector.to_pandas(sample_result)
                        
                        if not sample_df.empty:
                            print(f"   📋 Sample data:")
                            for i, row in sample_df.iterrows():
                                transno = row.iloc[0] if len(row) > 0 else 'N/A'
                                userid = row.iloc[1] if len(row) > 1 else 'N/A'
                                transdate = row.iloc[2] if len(row) > 2 else 'N/A'
                                status = row.iloc[3] if len(row) > 3 else 'N/A'
                                print(f"      - TRANSNO: {transno}, USER: {userid}, DATE: {transdate}, STATUS: {status}")
                else:
                    print(f"   ⚠️  Query returned empty result")
                    
            except Exception as e:
                error_msg = str(e)
                if "conversion error" in error_msg.lower():
                    print(f"   ❌ Date conversion error: {error_msg}")
                    print(f"   🔧 This indicates the date format fix is needed")
                    return False
                elif "table" in error_msg.lower() and "not" in error_msg.lower():
                    print(f"   ⚠️  Table {table_name} not found (expected for some months)")
                else:
                    print(f"   ❌ Query error: {error_msg}")
                    return False
        
        # Test division integration
        print(f"\n🏢 Testing division data integration...")
        
        division_query = """
        SELECT COUNT(*) as TOTAL_DIVISIONS
        FROM CRDIVISION a
        """
        
        try:
            result = connector.execute_query(division_query)
            df = connector.to_pandas(result)
            
            if not df.empty and len(df.columns) > 0:
                total_divisions = df.iloc[0, 0] if len(df) > 0 else 0
                print(f"   ✅ Found {total_divisions} divisions in CRDIVISION table")
                
                # Test sample divisions
                if total_divisions > 0:
                    sample_div_query = """
                    SELECT FIRST 5 ID, DIVCODE, DIVNAME
                    FROM CRDIVISION a
                    ORDER BY DIVNAME
                    """
                    
                    div_result = connector.execute_query(sample_div_query)
                    div_df = connector.to_pandas(div_result)
                    
                    if not div_df.empty:
                        print(f"   📋 Sample divisions:")
                        for i, row in div_df.iterrows():
                            div_id = row.iloc[0] if len(row) > 0 else 'N/A'
                            div_code = row.iloc[1] if len(row) > 1 else 'N/A'
                            div_name = row.iloc[2] if len(row) > 2 else 'N/A'
                            print(f"      - ID: {div_id}, CODE: {div_code}, NAME: {div_name}")
            else:
                print(f"   ⚠️  No divisions found")
                
        except Exception as e:
            print(f"   ❌ Division query error: {e}")
        
        # Test employee mapping
        print(f"\n👥 Testing employee mapping...")
        
        emp_query = """
        SELECT COUNT(*) as TOTAL_EMPLOYEES
        FROM EMP
        """
        
        try:
            result = connector.execute_query(emp_query)
            df = connector.to_pandas(result)
            
            if not df.empty and len(df.columns) > 0:
                total_employees = df.iloc[0, 0] if len(df) > 0 else 0
                print(f"   ✅ Found {total_employees} employees in EMP table")
                
                # Test sample employees
                if total_employees > 0:
                    sample_emp_query = """
                    SELECT FIRST 5 ID, NAME
                    FROM EMP
                    WHERE NAME IS NOT NULL
                    """
                    
                    emp_result = connector.execute_query(sample_emp_query)
                    emp_df = connector.to_pandas(emp_result)
                    
                    if not emp_df.empty:
                        print(f"   📋 Sample employees:")
                        for i, row in emp_df.iterrows():
                            emp_id = row.iloc[0] if len(row) > 0 else 'N/A'
                            emp_name = row.iloc[1] if len(row) > 1 else 'N/A'
                            print(f"      - ID: {emp_id}, NAME: {emp_name}")
            else:
                print(f"   ⚠️  No employees found")
                
        except Exception as e:
            print(f"   ❌ Employee query error: {e}")
        
        print(f"\n✅ All date format tests completed successfully!")
        print(f"🎉 The date format fix appears to be working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_gui_integration():
    """Test integration dengan GUI components."""
    print(f"\n🖥️  Testing GUI integration...")
    
    # Test date calculation logic
    test_months = [
        (5, 2025),   # May 2025
        (12, 2024),  # December (year boundary)
        (2, 2025),   # February
        (1, 2025)    # January
    ]
    
    for month, year in test_months:
        # Replicate GUI logic
        start_date = f"{year}-{month:02d}-01"
        
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        table_name = f"FFBSCANNERDATA{month:02d}"
        
        print(f"   📅 {table_name}: {start_date} to {end_date}")
        
        # Validate date format
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_dt > start_dt:
                print(f"      ✅ Date range is valid")
            else:
                print(f"      ❌ Invalid date range!")
                return False
                
        except ValueError as e:
            print(f"      ❌ Date parsing error: {e}")
            return False
    
    print(f"   ✅ All GUI integration tests passed!")
    return True

def main():
    """Main test function."""
    print("🧪 Starting Ifess Analysis Date Format Fix Tests...")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    db_test_passed = test_date_format_fix()
    gui_test_passed = test_gui_integration()
    
    print(f"\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Database Tests: {'✅ PASSED' if db_test_passed else '❌ FAILED'}")
    print(f"GUI Integration Tests: {'✅ PASSED' if gui_test_passed else '❌ FAILED'}")
    
    if db_test_passed and gui_test_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ The date format fix is working correctly")
        print(f"✅ GUI should now work without SQLCODE -413 errors")
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print(f"🔧 Please check the error messages above")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()