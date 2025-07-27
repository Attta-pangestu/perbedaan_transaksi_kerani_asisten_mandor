#!/usr/bin/env python3
"""
Test script untuk GUI Multi-Estate FFB Analysis
Memverifikasi dependencies dan basic functionality
"""

import sys
import os

def test_dependencies():
    """Test required dependencies"""
    print("Testing dependencies...")
    
    try:
        import tkinter as tk
        print("✓ tkinter - OK")
    except ImportError:
        print("✗ tkinter - MISSING")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas - OK")
    except ImportError:
        print("✗ pandas - MISSING")
        print("  Install: pip install pandas")
        return False
    
    try:
        from tkcalendar import DateEntry
        print("✓ tkcalendar - OK")
    except ImportError:
        print("✗ tkcalendar - MISSING")
        print("  Install: pip install tkcalendar")
        return False
    
    try:
        import fdb
        print("✓ fdb (firebird) - OK")
    except ImportError:
        print("✗ fdb - MISSING")
        print("  Install: pip install fdb")
        return False
    
    try:
        import reportlab
        print("✓ reportlab - OK")
    except ImportError:
        print("✗ reportlab - MISSING")
        print("  Install: pip install reportlab")
        return False
    
    return True

def test_files():
    """Test required files"""
    print("\nTesting required files...")
    
    required_files = [
        'gui_multi_estate_ffb_analysis.py',
        'firebird_connector.py',
        'run_multi_estate_gui.bat'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} - EXISTS")
        else:
            print(f"✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_estate_paths():
    """Test estate database paths"""  
    print("\nTesting estate database paths...")
    
    ESTATES = {
        "PGE 1A": r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB",
        "PGE 1B": r"C:\Users\nbgmf\Downloads\PTRJ_P1B\PTRJ_P1B.FDB",
        "PGE 2A": r"C:\Users\nbgmf\Downloads\IFESS_PGE_2A_19-06-2025",
        "PGE 2B": r"C:\Users\nbgmf\Downloads\IFESS_2B_19-06-2025\PTRJ_P2B.FDB",
        "IJL": r"C:\Users\nbgmf\Downloads\IFESS_IJL_19-06-2025\PTRJ_IJL_IMPIANJAYALESTARI.FDB",
        "DME": r"C:\Users\nbgmf\Downloads\IFESS_DME_19-06-2025\PTRJ_DME.FDB",
        "Are B2": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B2_19-06-2025\PTRJ_AB2.FDB",
        "Are B1": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B1_19-06-2025\PTRJ_AB1.FDB",
        "Are A": r"C:\Users\nbgmf\Downloads\IFESS_ARE_A_19-06-2025\PTRJ_ARA.FDB",
        "Are C": r"C:\Users\nbgmf\Downloads\IFESS_ARE_C_19-06-2025\PTRJ_ARC.FDB"
    }
    
    available_count = 0
    for estate_name, db_path in ESTATES.items():
        # Handle folder path (like PGE 2A)
        if os.path.isdir(db_path):
            # Look for .FDB file in folder
            fdb_found = False
            try:
                for file in os.listdir(db_path):
                    if file.upper().endswith('.FDB'):
                        actual_path = os.path.join(db_path, file)
                        if os.path.exists(actual_path):
                            print(f"✓ {estate_name} - FOUND: {file}")
                            available_count += 1
                            fdb_found = True
                            break
                
                if not fdb_found:
                    print(f"✗ {estate_name} - NO FDB FILE IN FOLDER")
            except OSError:
                print(f"✗ {estate_name} - FOLDER NOT ACCESSIBLE")
        elif os.path.exists(db_path):
            print(f"✓ {estate_name} - AVAILABLE")
            available_count += 1
        else:
            print(f"✗ {estate_name} - NOT FOUND")
    
    print(f"\nAvailable estates: {available_count}/{len(ESTATES)}")
    return available_count > 0

def test_gui_import():
    """Test GUI import"""
    print("\nTesting GUI import...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        from gui_multi_estate_ffb_analysis import MultiEstateFFBAnalysisGUI
        print("✓ GUI class import - OK")
        return True
    except ImportError as e:
        print(f"✗ GUI class import - FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ GUI class import - ERROR: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("MULTI-ESTATE FFB GUI TEST - PDF VERSION")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Dependencies", test_dependencies),
        ("Required Files", test_files),
        ("Estate Paths", test_estate_paths),
        ("GUI Import", test_gui_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[TEST: {test_name}]")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! GUI ready to run.")
        print("Execute: run_multi_estate_gui.bat")
        print("Output: PDF report with detailed table")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running GUI.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    
    # Keep window open
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1) 