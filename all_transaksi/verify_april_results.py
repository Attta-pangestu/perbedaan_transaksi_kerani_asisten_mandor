#!/usr/bin/env python3
"""
Script untuk memverifikasi hasil analisis April 2025 dengan data ekspektasi
"""

import os
import sys
import pandas as pd
from datetime import datetime

from firebird_connector import FirebirdConnector
from analisis_mandor_per_divisi_corrected import (
    get_employee_mapping, 
    get_division_list, 
    analyze_division_transactions
)

# Konfigurasi database
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def run_april_analysis():
    """Jalankan analisis untuk April 2025 dan bandingkan dengan ekspektasi."""
    print("VERIFIKASI HASIL ANALISIS APRIL 2025")
    print("="*60)
    print("Comparing with expected verification data...")
    print("="*60)
    
    try:
        # Setup database connection
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # Load employee mapping
        employee_mapping = get_employee_mapping(connector)
        
        # Get division list
        divisions = get_division_list(connector)
        
        if not divisions:
            print("✗ No divisions found!")
            return
        
        print(f"✓ Found {len(divisions)} divisions")
        
        # Expected data from user
        expected_divisions = {
            'Air Batu': {
                'total_receipts': 2322,
                'mandore_verification': 13.52,
                'assistant_verification': 12.10
            },
            'Air Kundo': {
                'total_receipts': 264,
                'mandore_verification': 5.30,
                'assistant_verification': 0.76
            },
            'Air Hijau': {
                'total_receipts': 2008,
                'mandore_verification': 14.79,
                'assistant_verification': 9.21
            }
        }
        
        print("\nAnalyzing each division for April 2025...")
        
        for division in divisions:
            div_id = division['div_id']
            div_name = division['div_name']
            div_code = division['div_code']
            
            # Skip divisions not in our expected list
            if div_name not in expected_divisions:
                continue
            
            print(f"\n{'='*50}")
            print(f"DIVISION: {div_name} ({div_code})")
            print(f"{'='*50}")
            
            # Run analysis
            result = analyze_division_transactions(
                connector, employee_mapping, div_id, div_name, month=4, year=2025)
            
            if not result:
                print(f"  ✗ No data found for division {div_name}")
                continue
            
            # Get results
            role_stats = result['role_stats']
            total_transactions = result['total_transactions']
            
            # Calculate verification rates
            mandor_verified = sum(emp['verified_transactions'] for emp in role_stats.get('MANDOR', {}).values())
            asisten_verified = sum(emp['verified_transactions'] for emp in role_stats.get('ASISTEN', {}).values())
            
            mandor_rate = (mandor_verified / total_transactions * 100) if total_transactions > 0 else 0
            asisten_rate = (asisten_verified / total_transactions * 100) if total_transactions > 0 else 0
            
            # Get expected values
            expected = expected_divisions[div_name]
            expected_total = expected['total_receipts']
            expected_mandor = expected['mandore_verification']
            expected_asisten = expected['assistant_verification']
            
            # Print comparison
            print(f"Total Receipts:")
            print(f"  Actual: {total_transactions}")
            print(f"  Expected: {expected_total}")
            if abs(total_transactions - expected_total) <= 10:
                print(f"  ✓ MATCH (difference: {abs(total_transactions - expected_total)})")
            else:
                print(f"  ✗ MISMATCH (difference: {abs(total_transactions - expected_total)})")
            
            print(f"\nMandore Verification Rate:")
            print(f"  Actual: {mandor_rate:.2f}%")
            print(f"  Expected: {expected_mandor:.2f}%")
            if abs(mandor_rate - expected_mandor) <= 1.0:
                print(f"  ✓ MATCH (difference: {abs(mandor_rate - expected_mandor):.2f}%)")
            else:
                print(f"  ✗ MISMATCH (difference: {abs(mandor_rate - expected_mandor):.2f}%)")
            
            print(f"\nAsisten Verification Rate:")
            print(f"  Actual: {asisten_rate:.2f}%")
            print(f"  Expected: {expected_asisten:.2f}%")
            if abs(asisten_rate - expected_asisten) <= 1.0:
                print(f"  ✓ MATCH (difference: {abs(asisten_rate - expected_asisten):.2f}%)")
            else:
                print(f"  ✗ MISMATCH (difference: {abs(asisten_rate - expected_asisten):.2f}%)")
            
            # Show employee details
            print(f"\nEmployee Details:")
            for role, employees in role_stats.items():
                if employees:
                    print(f"  {role}:")
                    for emp_id, emp_data in employees.items():
                        name = emp_data['employee_name']
                        total = emp_data['total_transactions']
                        verified = emp_data['verified_transactions']
                        rate = (verified / total * 100) if total > 0 else 0
                        print(f"    - {name}: {total} total, {verified} verified ({rate:.1f}%)")
        
        print(f"\n{'='*60}")
        print("VERIFICATION COMPLETED")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_april_analysis() 