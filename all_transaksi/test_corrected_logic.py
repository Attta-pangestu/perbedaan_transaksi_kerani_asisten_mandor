#!/usr/bin/env python3
"""
Test script untuk memverifikasi logika yang sudah diperbaiki
Menghitung SEMUA transaksi tanpa filter status 704
"""

from firebird_connector import FirebirdConnector
from analisis_mandor_per_divisi_corrected import get_employee_mapping, analyze_division_transactions

DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"

def test_corrected_logic():
    """Test logika yang sudah diperbaiki"""
    print("TESTING CORRECTED LOGIC - TANPA FILTER STATUS")
    print("="*60)
    
    try:
        connector = FirebirdConnector(DB_PATH)
        
        if not connector.test_connection():
            print("✗ Database connection failed!")
            return
        
        print("✓ Database connection successful")
        
        # Get employee mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"✓ Loaded {len(employee_mapping)} employee mappings")
        
        # Test Air Kundo division
        div_id = '16'
        div_name = 'Air Kundo'
        month = 4
        year = 2025
        
        print(f"\nTesting {div_name} (ID: {div_id}) for {month:02d}/{year}")
        print("Menghitung SEMUA transaksi (tanpa filter status 704)")
        print("-" * 60)
        
        result = analyze_division_transactions(connector, employee_mapping, div_id, div_name, month, year)
        
        if result:
            role_stats = result['role_stats']
            verification_stats = result.get('verification_stats', {})
            
            total_kerani = verification_stats.get('total_kerani_transactions', 0)
            total_mandor = verification_stats.get('total_mandor_transactions', 0)
            total_asisten = verification_stats.get('total_asisten_transactions', 0)
            total_verifications = verification_stats.get('total_verifications', 0)
            
            print(f"📊 HASIL ANALISIS:")
            print(f"Total transaksi KERANI (PM): {total_kerani}")
            print(f"Total transaksi MANDOR (P1): {total_mandor}")
            print(f"Total transaksi ASISTEN (P5): {total_asisten}")
            print(f"Total verifikasi (P1+P5): {total_verifications}")
            
            if total_kerani > 0:
                verification_rate = (total_verifications / total_kerani * 100)
                mandor_contribution = (total_mandor / total_kerani * 100)
                asisten_contribution = (total_asisten / total_kerani * 100)
                
                print(f"\n📈 PERSENTASE:")
                print(f"Tingkat verifikasi: {verification_rate:.2f}%")
                print(f"Kontribusi MANDOR: {mandor_contribution:.2f}%")
                print(f"Kontribusi ASISTEN: {asisten_contribution:.2f}%")
            
            print(f"\n👥 DETAIL KARYAWAN:")
            
            # KERANI details
            kerani_data = role_stats.get('KERANI', {})
            if kerani_data:
                print(f"🔹 KERANI (PM transactions):")
                for emp_id, emp_data in kerani_data.items():
                    emp_name = emp_data['employee_name']
                    transactions = emp_data['total_transactions']
                    contribution = emp_data.get('contribution_percentage', 0)
                    
                    print(f"  {emp_name} (ID: {emp_id}): {transactions} transaksi ({contribution:.2f}%)")
                    
                    # Special check for Erly
                    if emp_id == '4771':
                        expected = 123
                        status = "✓ MATCH" if transactions == expected else f"✗ MISMATCH (expected {expected})"
                        print(f"    Expected: {expected} - {status}")
            
            # MANDOR details
            mandor_data = role_stats.get('MANDOR', {})
            if mandor_data:
                print(f"🔹 MANDOR (P1 transactions):")
                for emp_id, emp_data in mandor_data.items():
                    emp_name = emp_data['employee_name']
                    transactions = emp_data['total_transactions']
                    contribution = emp_data.get('contribution_percentage', 0)
                    print(f"  {emp_name} (ID: {emp_id}): {transactions} verifikasi ({contribution:.2f}%)")
            
            # ASISTEN details
            asisten_data = role_stats.get('ASISTEN', {})
            if asisten_data:
                print(f"🔹 ASISTEN (P5 transactions):")
                for emp_id, emp_data in asisten_data.items():
                    emp_name = emp_data['employee_name']
                    transactions = emp_data['total_transactions']
                    contribution = emp_data.get('contribution_percentage', 0)
                    print(f"  {emp_name} (ID: {emp_id}): {transactions} verifikasi ({contribution:.2f}%)")
            
            print(f"\n" + "="*60)
            print("FORMULA VERIFICATION:")
            print("="*60)
            print(f"Total KERANI (PM): {total_kerani}")
            print(f"Total MANDOR (P1): {total_mandor}")
            print(f"Total ASISTEN (P5): {total_asisten}")
            print(f"Total Verifikasi: {total_mandor} + {total_asisten} = {total_verifications}")
            print(f"Verification Rate: ({total_verifications} / {total_kerani}) × 100 = {verification_rate:.2f}%")
            
            print(f"\n📋 EXPECTED vs ACTUAL:")
            expected_data = {
                'total_kerani': 264,
                'erly_transactions': 123,
                'verification_rate_range': (5.0, 7.0)  # Expected range
            }
            
            print(f"Total KERANI: {total_kerani} (Expected: ~{expected_data['total_kerani']})")
            print(f"Erly transactions: Found in KERANI details above")
            print(f"Verification rate: {verification_rate:.2f}% (Expected: {expected_data['verification_rate_range'][0]:.1f}%-{expected_data['verification_rate_range'][1]:.1f}%)")
            
        else:
            print("✗ No analysis result returned")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_corrected_logic()
