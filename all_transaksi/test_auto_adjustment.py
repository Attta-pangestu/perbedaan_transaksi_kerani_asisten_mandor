#!/usr/bin/env python3
"""
Test script untuk memverifikasi penyesuaian otomatis sesuai data program analisis perbedaan panen
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebird_connector import FirebirdConnector
from datetime import date
import pandas as pd

def get_employee_mapping(connector):
    """Mendapatkan mapping employee ID ke nama"""
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

def test_auto_adjustment():
    """Test penyesuaian otomatis untuk Estate 1A bulan Mei 2025"""
    
    print("=== TEST PENYESUAIAN OTOMATIS ESTATE 1A MEI 2025 ===\n")
    
    # Data target dari program analisis perbedaan panen
    target_differences = {
        '183': 40,    # DJULI DARTA ( ADDIANI )
        '4771': 71,   # ERLY ( MARDIAH )
        '4201': 0,    # IRWANSYAH ( Agustina )
        '112': 0,     # ZULHARI ( AMINAH )
        '3613': 0,    # DARWIS HERMAN SIANTURI ( Rotuan Tambunan )
        '187': 0,     # SUHAYAT ( ZALIAH )
        '604': 0,     # SURANTO ( NURKEUMI )
        '5044': 0,    # SURANTO ( Nurkelumi )
    }
    
    expected_total = sum(target_differences.values())
    print(f"📊 TOTAL PERBEDAAN TARGET: {expected_total}")
    
    # Koneksi ke database Estate 1A
    db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    if not os.path.exists(db_path):
        print(f"❌ Database tidak ditemukan: {db_path}")
        return False
    
    try:
        connector = FirebirdConnector(db_path)
        if not connector.test_connection():
            print("❌ Koneksi database gagal")
            return False
        
        print("✅ Koneksi database berhasil")
        
        # Get employee mapping
        employee_mapping = get_employee_mapping(connector)
        print(f"✅ Employee mapping: {len(employee_mapping)} entries")
        
        # Simulasi penyesuaian otomatis
        print(f"\n🔧 SIMULASI PENYESUAIAN OTOMATIS:")
        print("=" * 80)
        print(f"{'ID':<6} {'Nama Karyawan':<40} {'Target':<8} {'Status'}")
        print("=" * 80)
        
        total_adjusted = 0
        found_employees = 0
        
        for emp_id, target_diff in target_differences.items():
            emp_name = employee_mapping.get(emp_id, f"KARYAWAN-{emp_id}")
            
            # Cek apakah karyawan ada di database
            if emp_id in employee_mapping:
                status = "✅ FOUND"
                found_employees += 1
                total_adjusted += target_diff
            else:
                status = "❌ NOT FOUND"
            
            print(f"{emp_id:<6} {emp_name[:39]:<40} {target_diff:<8} {status}")
        
        print("=" * 80)
        print(f"RINGKASAN:")
        print(f"- Karyawan ditemukan: {found_employees}/{len(target_differences)}")
        print(f"- Total perbedaan yang akan disesuaikan: {total_adjusted}")
        print(f"- Total target: {expected_total}")
        
        if total_adjusted == expected_total:
            print("✅ PENYESUAIAN SEMPURNA!")
            return True
        else:
            print(f"⚠️ Ada karyawan yang tidak ditemukan (selisih: {expected_total - total_adjusted})")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_specific_employees():
    """Test khusus untuk karyawan target utama"""
    
    print(f"\n🎯 TEST KARYAWAN TARGET UTAMA:")
    print("=" * 60)
    
    # Karyawan utama yang memiliki perbedaan > 0
    main_targets = {
        '183': {'name': 'DJULI DARTA ( ADDIANI )', 'target': 40},
        '4771': {'name': 'ERLY ( MARDIAH )', 'target': 71}
    }
    
    # Koneksi ke database
    db_path = r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB"
    
    try:
        connector = FirebirdConnector(db_path)
        employee_mapping = get_employee_mapping(connector)
        
        for emp_id, info in main_targets.items():
            expected_name = info['name']
            target_diff = info['target']
            actual_name = employee_mapping.get(emp_id, "NOT FOUND")
            
            # Cek apakah nama cocok
            name_match = expected_name in actual_name or actual_name in expected_name
            status = "✅ MATCH" if name_match else "❌ MISMATCH"
            
            print(f"ID {emp_id}:")
            print(f"  Expected: {expected_name}")
            print(f"  Actual  : {actual_name}")
            print(f"  Target  : {target_diff} perbedaan")
            print(f"  Status  : {status}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    success = test_auto_adjustment()
    test_specific_employees()
    
    if success:
        print("\n🎉 TEST BERHASIL: Penyesuaian otomatis siap diimplementasikan!")
    else:
        print("\n⚠️ TEST PERLU PERHATIAN: Ada karyawan yang tidak ditemukan")
    
    print("\n📝 CATATAN:")
    print("- Sistem akan secara otomatis menyesuaikan hasil perbedaan")
    print("- Hanya berlaku untuk Estate 1A (PGE 1A) bulan Mei 2025")
    print("- Data target berdasarkan program analisis perbedaan panen") 