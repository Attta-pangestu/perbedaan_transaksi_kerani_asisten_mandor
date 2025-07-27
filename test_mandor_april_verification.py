#!/usr/bin/env python3
"""
Script Test untuk Verifikasi Data Mandor Bulan April 2025
Memvalidasi apakah script analisis menghasilkan data yang sesuai dengan yang diharapkan
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add the all_transaksi directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'all_transaksi'))

from all_transaksi.firebird_connector import FirebirdConnector
from all_transaksi.analisis_mandor_per_divisi_corrected import (
    get_employee_mapping, 
    get_division_list, 
    analyze_division_transactions,
    get_employee_role_corrected
)

# Konfigurasi database
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

# Data ekspektasi dari user
EXPECTED_DATA = {
    'A1': {  # Air Batu
        'div_name': 'Air Batu',
        'total_receipts': 2322,
        'employees': {
            'DJULI DARTA (ADDIANI)': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 381},
            'ERLY ( MARDIAH )': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 1941},
            'SUHAYAT ( ZALIAH )': {'conductor': 314, 'assistant': 0, 'manager': 0, 'bunch_counter': 0},
            'SURANTO ( Nurkelumi )': {'conductor': 0, 'assistant': 281, 'manager': 0, 'bunch_counter': 0}
        },
        'verification_rates': {
            'manager': 0.00,
            'assistant': 12.10,
            'mandore': 13.52
        }
    },
    'A2': {  # Air Kundo
        'div_name': 'Air Kundo',
        'total_receipts': 264,
        'employees': {
            'DJULI DARTA (ADDIANI)': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 141},
            'ERLY ( MARDIAH )': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 123},
            'SUHAYAT ( ZALIAH )': {'conductor': 14, 'assistant': 0, 'manager': 0, 'bunch_counter': 0},
            'SURANTO ( Nurkelumi )': {'conductor': 0, 'assistant': 2, 'manager': 0, 'bunch_counter': 0}
        },
        'verification_rates': {
            'manager': 0.00,
            'assistant': 0.76,
            'mandore': 5.30
        }
    },
    'A3': {  # Air Hijau
        'div_name': 'Air Hijau',
        'total_receipts': 2008,
        'employees': {
            'DARWIS HERMAN': {'conductor': 0, 'assistant': 185, 'manager': 0, 'bunch_counter': 0},
            'IRWANSYAH ( Agustina )': {'conductor': 0, 'assistant': 0, 'manager': 0, 'bunch_counter': 1199},
            'ZULHARI ( AMINAH )': {'conductor': 297, 'assistant': 0, 'manager': 0, 'bunch_counter': 809}
        },
        'verification_rates': {
            'manager': 0.00,
            'assistant': 9.21,
            'mandore': 14.79
        }
    }
}

def test_database_connection(connector):
    """Test koneksi database."""
    print("Testing database connection...")
    if connector.test_connection():
        print("✓ Database connection successful")
        return True
    else:
        print("✗ Database connection failed")
        return False

def test_april_data_exists(connector):
    """Test apakah data FFBScannerData04 ada."""
    print("\nTesting April 2025 data availability...")
    
    query = """
    SELECT COUNT(*) as count
    FROM FFBSCANNERDATA04 
    WHERE TRANSDATE >= '2025-04-01' 
    AND TRANSDATE <= '2025-04-30'
    """
    
    try:
        result = connector.execute_query(query)
        df = connector.to_pandas(result)
        
        if not df.empty:
            count = df.iloc[0, 0]
            print(f"✓ Found {count} transactions in FFBScannerData04 for April 2025")
            return count > 0
        else:
            print("✗ No data found in FFBScannerData04 for April 2025")
            return False
    except Exception as e:
        print(f"✗ Error checking April data: {e}")
        return False

def analyze_april_divisions(connector):
    """Analisis divisi untuk bulan April 2025."""
    print("\nAnalyzing divisions for April 2025...")
    
    # Load employee mapping
    employee_mapping = get_employee_mapping(connector)
    
    # Get division list
    divisions = get_division_list(connector)
    
    if not divisions:
        print("✗ No divisions found!")
        return {}
    
    print(f"Found {len(divisions)} divisions")
    
    # Analyze each division for April
    division_results = {}
    
    for division in divisions:
        div_id = division['div_id']
        div_name = division['div_name']
        div_code = division['div_code']
        
        print(f"\nAnalyzing division: {div_name} ({div_code})")
        
        result = analyze_division_transactions(
            connector, employee_mapping, div_id, div_name, month=4, year=2025)
        
        if result:
            division_results[div_code] = result
            
            # Print summary
            role_stats = result['role_stats']
            total_transactions = result['total_transactions']
            
            print(f"  Total transactions: {total_transactions}")
            print(f"  KERANI employees: {len(role_stats.get('KERANI', {}))}")
            print(f"  MANDOR employees: {len(role_stats.get('MANDOR', {}))}")
            print(f"  ASISTEN employees: {len(role_stats.get('ASISTEN', {}))}")
            
            # Show detailed breakdown per employee
            for role, employees in role_stats.items():
                if employees:
                    print(f"    {role}:")
                    for emp_id, emp_data in employees.items():
                        name = emp_data['employee_name']
                        total = emp_data['total_transactions']
                        verified = emp_data['verified_transactions']
                        print(f"      - {name}: {total} total, {verified} verified")
        else:
            print(f"  No data found for division {div_name}")
    
    return division_results

def compare_with_expected(division_results):
    """Bandingkan hasil dengan data ekspektasi."""
    print("\n" + "="*80)
    print("COMPARISON WITH EXPECTED DATA")
    print("="*80)
    
    all_match = True
    
    for div_code, expected in EXPECTED_DATA.items():
        print(f"\nDivision {div_code} ({expected['div_name']}):")
        
        if div_code not in division_results:
            print(f"  ✗ Division {div_code} not found in results")
            all_match = False
            continue
        
        actual = division_results[div_code]
        role_stats = actual['role_stats']
        
        # Check total receipts
        actual_total = actual['total_transactions']
        expected_total = expected['total_receipts']
        
        if abs(actual_total - expected_total) < 10:  # Allow small differences
            print(f"  ✓ Total receipts: {actual_total} (expected: {expected_total})")
        else:
            print(f"  ✗ Total receipts: {actual_total} (expected: {expected_total})")
            all_match = False
        
        # Check employees
        print("  Employee comparison:")
        for exp_name, exp_data in expected['employees'].items():
            found_employee = False
            
            # Search in all roles
            for role, employees in role_stats.items():
                for emp_id, emp_data in employees.items():
                    actual_name = emp_data['employee_name']
                    
                    # Fuzzy match employee names
                    if (exp_name.upper().replace(' ', '') in actual_name.upper().replace(' ', '') or
                        actual_name.upper().replace(' ', '') in exp_name.upper().replace(' ', '')):
                        
                        found_employee = True
                        total_tx = emp_data['total_transactions']
                        verified_tx = emp_data['verified_transactions']
                        
                        print(f"    ✓ Found {actual_name} (role: {role})")
                        print(f"      Total: {total_tx}, Verified: {verified_tx}")
                        
                        # Map role to activity type
                        if role == 'KERANI':
                            print(f"      Bunch Counter: {total_tx} (expected: {exp_data['bunch_counter']})")
                        elif role == 'MANDOR':
                            print(f"      Conductor: {verified_tx} (expected: {exp_data['conductor']})")
                        elif role == 'ASISTEN':
                            print(f"      Assistant: {verified_tx} (expected: {exp_data['assistant']})")
                        break
                if found_employee:
                    break
            
            if not found_employee:
                print(f"    ✗ Employee not found: {exp_name}")
                all_match = False
        
        # Calculate verification rates
        total_receipts = actual['total_transactions']
        mandor_verified = sum(emp['verified_transactions'] for emp in role_stats.get('MANDOR', {}).values())
        asisten_verified = sum(emp['verified_transactions'] for emp in role_stats.get('ASISTEN', {}).values())
        
        mandor_rate = (mandor_verified / total_receipts * 100) if total_receipts > 0 else 0
        asisten_rate = (asisten_verified / total_receipts * 100) if total_receipts > 0 else 0
        
        print(f"  Verification rates:")
        print(f"    Manager: 0.00% (expected: {expected['verification_rates']['manager']:.2f}%)")
        print(f"    Assistant: {asisten_rate:.2f}% (expected: {expected['verification_rates']['assistant']:.2f}%)")
        print(f"    Mandore: {mandor_rate:.2f}% (expected: {expected['verification_rates']['mandore']:.2f}%)")
    
    if all_match:
        print("\n✓ ALL DATA MATCHES EXPECTATIONS!")
    else:
        print("\n✗ Some data doesn't match expectations - review needed")
    
    return all_match

def main():
    """Fungsi utama untuk test verifikasi."""
    print("FFB VERIFICATION TEST - APRIL 2025")
    print("="*50)
    print("Testing data against expected verification results")
    print("="*50)
    
    try:
        # Setup database connection
        connector = FirebirdConnector(DB_PATH)
        
        # Run tests
        if not test_database_connection(connector):
            return
        
        if not test_april_data_exists(connector):
            return
        
        # Analyze divisions
        division_results = analyze_april_divisions(connector)
        
        if not division_results:
            print("No division results to compare!")
            return
        
        # Compare with expected data
        compare_with_expected(division_results)
        
        print("\n" + "="*50)
        print("TEST COMPLETED")
        print("="*50)
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 