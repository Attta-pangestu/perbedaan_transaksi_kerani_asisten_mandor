#!/usr/bin/env python3
"""
Quick test untuk memverifikasi GUI akan menunjukkan Erly = 123
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

def test_gui_logic():
    """Test logic yang akan digunakan GUI"""
    print("TESTING GUI LOGIC")
    print("="*30)
    
    try:
        from correct_analysis_engine import analyze_multiple_divisions
        from firebird_connector import FirebirdConnector
        
        DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
        
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("❌ Database connection failed!")
            return
        
        print("✅ Database connected")
        
        # Test dengan parameter yang sama seperti GUI
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 28)  # GUI menggunakan end date ini
        
        divisions = [{'div_id': '16', 'div_name': 'Air Kundo'}]
        
        print(f"Testing analysis: {start_date} to {end_date}")
        
        results = analyze_multiple_divisions(connector, divisions, start_date, end_date)
        
        if results and len(results) > 0:
            result = results[0]
            employees = result['employees']
            stats = result['verification_stats']
            
            print(f"\nResults for Air Kundo:")
            print(f"Total KERANI: {stats['total_kerani_transactions']}")
            print(f"Total MANDOR: {stats['total_mandor_transactions']}")
            print(f"Total ASISTEN: {stats['total_asisten_transactions']}")
            print(f"Verification Rate: {stats['verification_rate']:.2f}%")
            
            if '4771' in employees:
                erly_pm = employees['4771']['PM']
                erly_name = employees['4771']['name']
                
                print(f"\n🎯 ERLY VERIFICATION:")
                print(f"Name: {erly_name}")
                print(f"ID: 4771")
                print(f"PM Transactions: {erly_pm}")
                print(f"Expected: 123")
                
                if erly_pm == 123:
                    print("✅ SUCCESS! GUI will show Erly = 123")
                    
                    # Simulate GUI display format
                    print(f"\n📊 GUI Display Format:")
                    print(f"Air Kundo\t{erly_name}\t4771\tKERANI\t0\t0\t0\t{erly_pm}")
                    
                    return True
                else:
                    print(f"❌ FAIL! GUI will show Erly = {erly_pm}")
                    return False
            else:
                print("❌ Erly (4771) not found in results")
                print("Available employees:")
                for emp_id, emp_data in employees.items():
                    if emp_data['PM'] > 0:
                        print(f"  {emp_id}: {emp_data['name']} - {emp_data['PM']} PM")
                return False
        else:
            print("❌ No results from analysis")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test"""
    print("QUICK GUI TEST")
    print("="*50)
    print("Testing if GUI will show correct Erly value...")
    print("="*50)
    
    success = test_gui_logic()
    
    print("\n" + "="*50)
    if success:
        print("🎉 TEST PASSED!")
        print("✅ GUI will show: Erly = 123 transactions")
        print("✅ System is working correctly")
        print("\nYou can now run: python run_simple_gui.py")
        print("Or double-click: run_gui.bat")
    else:
        print("❌ TEST FAILED!")
        print("❌ GUI will still show incorrect value")
        print("❌ Need to check analysis engine")
    
    return success

if __name__ == "__main__":
    main()
