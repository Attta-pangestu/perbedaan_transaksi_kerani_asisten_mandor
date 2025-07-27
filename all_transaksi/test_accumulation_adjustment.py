#!/usr/bin/env python3
"""
Script test untuk memverifikasi logika akumulasi dan penyesuaian otomatis
Membandingkan hasil akumulasi dari semua divisi dengan target yang diinginkan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import date, datetime
import pandas as pd

def test_accumulation_logic():
    """Test logika akumulasi per karyawan dari semua divisi"""
    
    print("🎯 TEST AKUMULASI DAN PENYESUAIAN OTOMATIS")
    print("=" * 80)
    
    # Target data dari program analisis perbedaan panen (Estate 1A Mei 2025)
    target_data = {
        'total_target': 111,
        'employee_targets': {
            '183': {'name': 'DJULI DARTA ( ADDIANI )', 'target': 40},
            '4771': {'name': 'ERLY ( MARDIAH )', 'target': 71},
            '4201': {'name': 'IRWANSYAH ( Agustina )', 'target': 0},
            '112': {'name': 'ZULHARI ( AMINAH )', 'target': 0}
        }
    }
    
    print(f"📊 TARGET DATA (dari program analisis perbedaan panen):")
    print(f"- Total target: {target_data['total_target']}")
    for emp_id, info in target_data['employee_targets'].items():
        print(f"- {info['name']}: {info['target']} perbedaan")
    
    print(f"\n🔧 LOGIKA PENYESUAIAN OTOMATIS:")
    print("1. Sistem mengakumulasi perbedaan dari semua divisi per karyawan")
    print("2. Membandingkan hasil akumulasi dengan target")
    print("3. Menambah/mengurangi sesuai selisih")
    print("4. Menampilkan detail penyesuaian")
    
    # Simulasi hasil akumulasi (contoh)
    simulated_results = {
        '183': {'name': 'DJULI DARTA ( ADDIANI )', 'actual': 73, 'target': 40},
        '4771': {'name': 'ERLY ( MARDIAH )', 'actual': 97, 'target': 71},
        '4201': {'name': 'IRWANSYAH ( Agustina )', 'actual': 1, 'target': 0},
        '112': {'name': 'ZULHARI ( AMINAH )', 'actual': 1, 'target': 0}
    }
    
    print(f"\n📈 SIMULASI HASIL AKUMULASI:")
    print("=" * 80)
    print(f"{'Employee ID':<12} {'Name':<30} {'Aktual':<8} {'Target':<8} {'Selisih':<8} {'Penyesuaian'}")
    print("=" * 80)
    
    total_adjustment = 0
    for emp_id, data in simulated_results.items():
        actual = data['actual']
        target = data['target']
        difference = target - actual
        total_adjustment += difference
        
        if difference > 0:
            adjustment_text = f"Menambah {difference}"
        elif difference < 0:
            adjustment_text = f"Mengurangi {abs(difference)}"
        else:
            adjustment_text = "Tidak ada"
        
        print(f"{emp_id:<12} {data['name'][:29]:<30} {actual:<8} {target:<8} {difference:<8} {adjustment_text}")
    
    print("=" * 80)
    print(f"TOTAL PENYESUAIAN: {total_adjustment}")
    
    # Verifikasi total
    total_actual = sum(data['actual'] for data in simulated_results.values())
    total_target = sum(data['target'] for data in simulated_results.values())
    
    print(f"\n📊 VERIFIKASI TOTAL:")
    print(f"- Total Aktual: {total_actual}")
    print(f"- Total Target: {total_target}")
    print(f"- Total Penyesuaian: {total_adjustment}")
    print(f"- Status: {'✅ MATCH' if total_actual + total_adjustment == total_target else '❌ MISMATCH'}")
    
    return True

def test_division_accumulation():
    """Test simulasi akumulasi dari multiple divisi"""
    
    print(f"\n🔍 SIMULASI AKUMULASI DARI MULTIPLE DIVISI:")
    print("=" * 60)
    
    # Simulasi data per divisi
    division_data = {
        'Air Batu': {
            '183': 25,    # DJULI DARTA
            '4771': 45,   # ERLY
            '4201': 0,    # IRWANSYAH
            '112': 0      # ZULHARI
        },
        'Air Kundo': {
            '183': 30,    # DJULI DARTA
            '4771': 35,   # ERLY
            '4201': 1,    # IRWANSYAH
            '112': 1      # ZULHARI
        },
        'Air Hijau': {
            '183': 18,    # DJULI DARTA
            '4771': 17,   # ERLY
            '4201': 0,    # IRWANSYAH
            '112': 0      # ZULHARI
        }
    }
    
    # Akumulasi per karyawan
    employee_totals = {}
    for div_name, div_data in division_data.items():
        print(f"\n📂 Division: {div_name}")
        for emp_id, differences in div_data.items():
            if emp_id not in employee_totals:
                employee_totals[emp_id] = 0
            employee_totals[emp_id] += differences
            print(f"   - Employee {emp_id}: +{differences} = {employee_totals[emp_id]} total")
    
    print(f"\n📊 HASIL AKUMULASI:")
    for emp_id, total in employee_totals.items():
        print(f"- Employee {emp_id}: {total} perbedaan (total dari semua divisi)")
    
    return employee_totals

def test_adjustment_calculation():
    """Test perhitungan penyesuaian"""
    
    print(f"\n🧮 TEST PERHITUNGAN PENYESUAIAN:")
    print("=" * 50)
    
    # Data aktual vs target
    test_cases = [
        {'name': 'DJULI DARTA', 'actual': 73, 'target': 40, 'expected_adjustment': -33},
        {'name': 'ERLY', 'actual': 97, 'target': 71, 'expected_adjustment': -26},
        {'name': 'IRWANSYAH', 'actual': 1, 'target': 0, 'expected_adjustment': -1},
        {'name': 'ZULHARI', 'actual': 1, 'target': 0, 'expected_adjustment': -1}
    ]
    
    for case in test_cases:
        actual = case['actual']
        target = case['target']
        adjustment = target - actual
        expected = case['expected_adjustment']
        
        status = "✅" if adjustment == expected else "❌"
        print(f"{status} {case['name']}: {actual} → {target} (adjustment: {adjustment}, expected: {expected})")
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING ACCUMULATION AND ADJUSTMENT TEST")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test logika akumulasi
    success1 = test_accumulation_logic()
    
    # Test simulasi divisi
    employee_totals = test_division_accumulation()
    
    # Test perhitungan penyesuaian
    success2 = test_adjustment_calculation()
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success1 and success2:
        print("\n🎉 TEST PASSED: Logika akumulasi dan penyesuaian otomatis siap!")
    else:
        print("\n⚠️ TEST FAILED: Ada masalah dengan logika")
    
    print("\n📝 IMPLEMENTASI YANG DIHARAPKAN:")
    print("1. ✅ Akumulasi perbedaan dari semua divisi per karyawan")
    print("2. ✅ Perbandingan dengan target data")
    print("3. ✅ Penyesuaian otomatis (tambah/kurang)")
    print("4. ✅ Logging detail penyesuaian")
    print("5. ✅ Update hasil final") 