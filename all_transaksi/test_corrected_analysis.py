#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan analisis
Khusus untuk memastikan Erly (SCANUSERID 4771) menunjukkan 123 transaksi
"""

import os
import sys
from firebird_connector import FirebirdConnector
from analisis_mandor_per_divisi_corrected import get_employee_mapping, analyze_division_transactions

# Database configuration
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def test_corrected_analysis():
    """Test analisis yang sudah diperbaiki"""
    print("TESTING CORRECTED ANALYSIS - AIR KUNDO")
    print("="*60)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # Get employee mapping
        print("Loading employee mapping...")
        employee_mapping = get_employee_mapping(connector)
        print(f"✓ Loaded {len(employee_mapping)} employee mappings")
        
        # Test Air Kundo division
        div_id = '16'
        div_name = 'Air Kundo'
        month = 4
        year = 2025
        
        print(f"\nAnalyzing {div_name} (ID: {div_id}) for {month:02d}/{year}")
        print("-" * 50)
        
        result = analyze_division_transactions(connector, employee_mapping, div_id, div_name, month, year)
        
        if result:
            role_stats = result['role_stats']
            verification_stats = result.get('verification_stats', {})
            
            print(f"Total transactions: {result['total_transactions']}")
            print(f"Total receipts (PM): {verification_stats.get('total_receipts', 0)}")
            
            # Check KERANI (PM transactions)
            print(f"\nKERANI (PM transactions):")
            kerani_stats = role_stats.get('KERANI', {})
            
            total_kerani_transactions = 0
            for emp_id, emp_data in kerani_stats.items():
                emp_name = emp_data['employee_name']
                transactions = emp_data['total_transactions']
                total_kerani_transactions += transactions
                
                print(f"  {emp_name} (ID: {emp_id}): {transactions} transactions")
                
                # Special check for Erly (SCANUSERID 4771)
                if emp_id == '4771':
                    expected = 123
                    status = "✓ MATCH" if transactions == expected else f"✗ MISMATCH (expected {expected})"
                    print(f"    Expected: {expected} - {status}")
            
            print(f"Total KERANI transactions: {total_kerani_transactions}")
            
            # Check verification rates
            total_receipts = verification_stats.get('total_receipts', 0)
            if total_receipts > 0:
                mandor_rate = (verification_stats.get('mandor_verifications', 0) / total_receipts * 100)
                asisten_rate = (verification_stats.get('asisten_verifications', 0) / total_receipts * 100)
                
                print(f"\nVerification Rates:")
                print(f"  Mandore: {mandor_rate:.2f}%")
                print(f"  Assistant: {asisten_rate:.2f}%")
            
            # Check MANDOR (P1 transactions)
            print(f"\nMANDOR (P1 transactions):")
            mandor_stats = role_stats.get('MANDOR', {})
            for emp_id, emp_data in mandor_stats.items():
                emp_name = emp_data['employee_name']
                transactions = emp_data['total_transactions']
                verified = emp_data['verified_transactions']
                print(f"  {emp_name} (ID: {emp_id}): {transactions} total, {verified} verified")
            
            # Check ASISTEN (P5 transactions)
            print(f"\nASISTEN (P5 transactions):")
            asisten_stats = role_stats.get('ASISTEN', {})
            for emp_id, emp_data in asisten_stats.items():
                emp_name = emp_data['employee_name']
                transactions = emp_data['total_transactions']
                verified = emp_data['verified_transactions']
                print(f"  {emp_name} (ID: {emp_id}): {transactions} total, {verified} verified")
            
            print(f"\n" + "="*60)
            print("EXPECTED vs ACTUAL COMPARISON")
            print("="*60)
            
            expected_data = {
                'total_receipts': 264,
                'employees': {
                    'DJULI DARTA ( ADDIANI )': {'bunch_counter': 141},
                    'ERLY ( MARDIAH )': {'bunch_counter': 123},
                    'SUHAYAT ( ZALIAH )': {'conductor': 14},
                    'SURANTO ( Nurkelumi )': {'assistant': 2}
                }
            }
            
            print(f"Total Receipts: {total_receipts} (Expected: {expected_data['total_receipts']})")
            
            # Check each expected employee
            for expected_name, expected_counts in expected_data['employees'].items():
                found = False
                for role_name, role_data in role_stats.items():
                    for emp_id, emp_data in role_data.items():
                        emp_name = emp_data['employee_name']
                        if expected_name in emp_name or emp_name in expected_name:
                            found = True
                            transactions = emp_data['total_transactions']
                            verified = emp_data['verified_transactions']
                            
                            if 'bunch_counter' in expected_counts:
                                expected_count = expected_counts['bunch_counter']
                                status = "✓ MATCH" if transactions == expected_count else f"✗ DIFF: {transactions - expected_count}"
                                print(f"{emp_name}: {transactions} Bunch Counter (Expected: {expected_count}) - {status}")
                            elif 'conductor' in expected_counts:
                                expected_count = expected_counts['conductor']
                                status = "✓ MATCH" if verified == expected_count else f"✗ DIFF: {verified - expected_count}"
                                print(f"{emp_name}: {verified} Conductor (Expected: {expected_count}) - {status}")
                            elif 'assistant' in expected_counts:
                                expected_count = expected_counts['assistant']
                                status = "✓ MATCH" if verified == expected_count else f"✗ DIFF: {verified - expected_count}"
                                print(f"{emp_name}: {verified} Assistant (Expected: {expected_count}) - {status}")
                            break
                    if found:
                        break
                
                if not found:
                    print(f"{expected_name}: NOT FOUND")
            
        else:
            print("✗ No analysis result returned")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_corrected_analysis()
