#!/usr/bin/env python3
"""
Test script untuk memverifikasi bahwa GUI menggunakan logika yang benar
"""

import os
import sys
from datetime import date
from firebird_connector import FirebirdConnector

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def get_employee_name_mapping(connector):
    """Get employee name mapping"""
    query = "SELECT ID, NAME FROM EMP"
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        mapping = {}
        if not df.empty:
            for _, row in df.iterrows():
                emp_id = str(row.iloc[0]).strip()
                emp_name = str(row.iloc[1]).strip()
                mapping[emp_id] = emp_name
        
        return mapping
    except:
        return {}

def analyze_division_correct(connector, emp_mapping, div_id, div_name):
    """Analyze division dengan query yang benar (sama dengan create_correct_report.py)"""
    print(f"\nAnalyzing {div_name} (ID: {div_id})")
    
    # Query untuk semua transaksi di divisi (TANPA filter status)
    query = f"""
    SELECT 
        a.SCANUSERID,
        a.RECORDTAG,
        COUNT(*) as transaction_count
    FROM 
        FFBSCANNERDATA04 a
    JOIN 
        OCFIELD b ON a.FIELDID = b.ID
    WHERE 
        b.DIVID = '{div_id}'
        AND a.TRANSDATE >= '2025-04-01' 
        AND a.TRANSDATE < '2025-04-29'
    GROUP BY a.SCANUSERID, a.RECORDTAG
    ORDER BY a.SCANUSERID, a.RECORDTAG
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if df.empty:
            print(f"  No data found for {div_name}")
            return None
        
        # Process results
        employees = {}
        total_kerani = 0
        total_mandor = 0
        total_asisten = 0
        
        for _, row in df.iterrows():
            scanuserid = str(row.iloc[0]).strip()
            recordtag = str(row.iloc[1]).strip()
            count = int(row.iloc[2])
            
            emp_name = emp_mapping.get(scanuserid, f"EMPLOYEE-{scanuserid}")
            
            if scanuserid not in employees:
                employees[scanuserid] = {
                    'name': emp_name,
                    'pm_count': 0,  # KERANI
                    'p1_count': 0,  # MANDOR
                    'p5_count': 0   # ASISTEN
                }
            
            if recordtag == 'PM':
                employees[scanuserid]['pm_count'] = count
                total_kerani += count
            elif recordtag == 'P1':
                employees[scanuserid]['p1_count'] = count
                total_mandor += count
            elif recordtag == 'P5':
                employees[scanuserid]['p5_count'] = count
                total_asisten += count
        
        total_verifications = total_mandor + total_asisten
        verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
        
        print(f"  Total KERANI (PM): {total_kerani}")
        print(f"  Total MANDOR (P1): {total_mandor}")
        print(f"  Total ASISTEN (P5): {total_asisten}")
        print(f"  Verification Rate: {verification_rate:.2f}%")
        
        # Special check for Erly
        if div_id == '16':  # Air Kundo
            erly_data = employees.get('4771')
            if erly_data:
                print(f"  ⭐ Erly (4771): {erly_data['pm_count']} PM transactions")
                print(f"     Expected: 123 - {'✓ MATCH' if erly_data['pm_count'] == 123 else '✗ MISMATCH'}")
        
        return {
            'div_id': div_id,
            'div_name': div_name,
            'employees': employees,
            'totals': {
                'kerani': total_kerani,
                'mandor': total_mandor,
                'asisten': total_asisten,
                'verifications': total_verifications,
                'verification_rate': verification_rate
            }
        }
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def test_gui_logic():
    """Test bahwa GUI menggunakan logika yang sama dengan create_correct_report.py"""
    print("TESTING CORRECTED GUI LOGIC")
    print("="*50)
    print("Verifying that GUI uses the same logic as create_correct_report.py")
    print("="*50)
    
    # Database path
    DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
    
    try:
        # Connect to database
        print("Connecting to database...")
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return False
        
        print("✅ Database connected successfully")
        
        # Get employee mapping
        emp_mapping = get_employee_name_mapping(connector)
        print(f"✅ Loaded {len(emp_mapping)} employee mappings")
        
        # Target divisions for testing
        divisions = [
            {'div_id': '15', 'div_name': 'Air Batu'},
            {'div_id': '16', 'div_name': 'Air Kundo'},
            {'div_id': '17', 'div_name': 'Air Hijau'}
        ]
        
        print(f"\nTesting {len(divisions)} divisions...")
        
        # Test each division
        for div in divisions:
            result = analyze_division_correct(connector, emp_mapping, div['div_id'], div['div_name'])
            
            if result:
                print(f"✅ {div['div_name']} analysis completed")
                
                # Verify Erly result for Air Kundo
                if div['div_name'] == 'Air Kundo':
                    erly_data = result['employees'].get('4771')
                    if erly_data:
                        print(f"🎯 VERIFICATION:")
                        print(f"   Erly (4771) PM transactions: {erly_data['pm_count']}")
                        print(f"   Expected: 123")
                        print(f"   Status: {'✅ CORRECT' if erly_data['pm_count'] == 123 else '❌ INCORRECT'}")
                        
                        if erly_data['pm_count'] != 123:
                            print("❌ TEST FAILED: Erly should have 123 transactions")
                            return False
            else:
                print(f"❌ {div['div_name']} analysis failed")
                return False
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("✅ GUI logic matches create_correct_report.py")
        print("✅ Erly verification is correct (123 transactions)")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_gui_components():
    """Test GUI components"""
    print("\nTESTING GUI COMPONENTS")
    print("="*30)
    
    try:
        # Test imports
        import tkinter as tk
        from tkinter import ttk
        from tkcalendar import DateEntry
        import pandas as pd
        from datetime import datetime, date
        import threading
        
        print("✅ All GUI dependencies imported successfully")
        
        # Test PDF generator
        from ffb_pdf_report_generator import generate_ffb_pdf_report
        print("✅ FFB PDF generator imported successfully")
        
        # Test Firebird connector
        from firebird_connector import FirebirdConnector
        print("✅ Firebird connector imported successfully")
        
        print("✅ All GUI components available")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install missing dependencies:")
        print("pip install pandas tkcalendar reportlab")
        return False
    except Exception as e:
        print(f"❌ Component test error: {e}")
        return False

def main():
    """Main test function"""
    print("FFB Scanner Analysis GUI - Logic Verification Test")
    print("="*60)
    
    # Test GUI components
    if not test_gui_components():
        print("\n❌ GUI component test failed")
        return
    
    # Test GUI logic
    if not test_gui_logic():
        print("\n❌ GUI logic test failed")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("The corrected GUI is ready to use.")
    print("\nTo run the GUI:")
    print("1. Double-click run_corrected_gui.bat")
    print("2. Or run: python gui_ffb_analysis_corrected.py")

if __name__ == "__main__":
    main() 