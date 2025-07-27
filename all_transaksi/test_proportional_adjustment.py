#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Verifikasi Logika Penyesuaian Proporsional
=======================================================

Script ini menguji logika penyesuaian proporsional untuk memastikan:
1. Penyesuaian didistribusikan secara proporsional ke setiap divisi
2. Total per karyawan sesuai dengan target yang diinginkan
3. Detail per divisi tetap terlihat realistis
"""

import sys
import os

# Tambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_proportional_adjustment():
    """Test logika penyesuaian proporsional"""
    
    print("🧪 TEST PENYESUAIAN PROPORSIONAL")
    print("=" * 50)
    
    # Simulasi data estate dengan beberapa divisi
    estate_results = [
        {
            'division': 'Air Batu 1',
            'employee_details': {
                'ERLY': {
                    'name': 'ERLY (Mardiah)',
                    'kerani_differences': 50,  # 50% dari total
                    'total_created': 100,
                    'total_verified': 30
                },
                'DJULI': {
                    'name': 'DJULI DARTA (Addiani)',
                    'kerani_differences': 30,  # 60% dari total
                    'total_created': 80,
                    'total_verified': 20
                }
            }
        },
        {
            'division': 'Air Batu 2', 
            'employee_details': {
                'ERLY': {
                    'name': 'ERLY (Mardiah)',
                    'kerani_differences': 35,  # 35% dari total
                    'total_created': 70,
                    'total_verified': 25
                },
                'DJULI': {
                    'name': 'DJULI DARTA (Addiani)',
                    'kerani_differences': 20,  # 40% dari total
                    'total_created': 50,
                    'total_verified': 15
                }
            }
        },
        {
            'division': 'Air Batu 3',
            'employee_details': {
                'ERLY': {
                    'name': 'ERLY (Mardiah)',
                    'kerani_differences': 12,  # 15% dari total
                    'total_created': 30,
                    'total_verified': 8
                },
                'DJULI': {
                    'name': 'DJULI DARTA (Addiani)',
                    'kerani_differences': 0,  # 0% dari total
                    'total_created': 20,
                    'total_verified': 10
                }
            }
        }
    ]
    
    # Target yang diinginkan
    target_differences = {
        'ERLY': 71,    # Aktual: 50+35+12=97, perlu dikurangi 26
        'DJULI': 40    # Aktual: 30+20+0=50, perlu dikurangi 10
    }
    
    print("📊 DATA AWAL:")
    print("-" * 30)
    
    # Hitung total awal per karyawan
    estate_employee_totals = {}
    for result in estate_results:
        div_name = result['division']
        print(f"\n📂 {div_name}:")
        for emp_id, emp_data in result['employee_details'].items():
            if emp_id not in estate_employee_totals:
                estate_employee_totals[emp_id] = {
                    'name': emp_data['name'],
                    'kerani_differences': 0
                }
            estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
            print(f"  👤 {emp_data['name']}: {emp_data['kerani_differences']} perbedaan")
    
    print(f"\n📈 TOTAL AWAL PER KARYAWAN:")
    for emp_id, emp_data in estate_employee_totals.items():
        print(f"  👤 {emp_data['name']}: {emp_data['kerani_differences']} perbedaan")
    
    print(f"\n🎯 TARGET YANG DIINGINKAN:")
    for emp_id, target in target_differences.items():
        print(f"  👤 {emp_id}: {target} perbedaan")
    
    print(f"\n🔧 PENYESUAIAN PROPORSIONAL:")
    print("-" * 30)
    
    # Implementasi logika penyesuaian proporsional
    total_adjustment = 0
    
    for emp_id, emp_data in estate_employee_totals.items():
        if emp_id in target_differences:
            original_total = emp_data['kerani_differences']
            target_total = target_differences[emp_id]
            
            # Hitung total penyesuaian yang diperlukan
            total_adjustment_needed = target_total - original_total
            
            if total_adjustment_needed != 0:
                print(f"\n👤 {emp_data['name']} (ID: {emp_id}):")
                print(f"  📊 Aktual: {original_total} → Target: {target_total}")
                print(f"  🔄 Penyesuaian: {total_adjustment_needed}")
                
                # Distribusikan penyesuaian secara proporsional ke setiap divisi
                adjustment_distribution = {}
                total_adjustment_calculated = 0
                
                # Hitung total perbedaan per divisi untuk karyawan ini
                divisional_totals = {}
                for result in estate_results:
                    div_name = result['division']
                    if emp_id in result['employee_details']:
                        div_diff = result['employee_details'][emp_id]['kerani_differences']
                        if div_diff > 0:
                            divisional_totals[div_name] = div_diff
                
                # Jika ada perbedaan di beberapa divisi, distribusikan secara proporsional
                if divisional_totals:
                    total_divisional = sum(divisional_totals.values())
                    print(f"  📂 Distribusi per divisi (Total: {total_divisional}):")
                    
                    # Hitung penyesuaian proporsional dengan penanganan pembulatan
                    adjustment_distribution = {}
                    total_adjustment_calculated = 0
                    
                    # Urutkan divisi berdasarkan proporsi (terbesar dulu)
                    sorted_divisions = sorted(divisional_totals.items(), key=lambda x: x[1], reverse=True)
                    
                    for i, (div_name, div_diff) in enumerate(sorted_divisions):
                        # Hitung proporsi penyesuaian untuk divisi ini
                        proportion = div_diff / total_divisional
                        
                        if i == len(sorted_divisions) - 1:
                            # Untuk divisi terakhir, gunakan sisa penyesuaian untuk menghindari pembulatan
                            adjustment_for_division = total_adjustment_needed - total_adjustment_calculated
                        else:
                            adjustment_for_division = round(total_adjustment_needed * proportion)
                            total_adjustment_calculated += adjustment_for_division
                        
                        adjustment_distribution[div_name] = adjustment_for_division
                        print(f"    📂 {div_name}: {div_diff} ({proportion:.1%}) → {adjustment_for_division}")
                    
                    # Terapkan penyesuaian ke setiap divisi
                    print(f"  ✅ Hasil penyesuaian:")
                    for result in estate_results:
                        div_name = result['division']
                        if div_name in adjustment_distribution:
                            emp_data_div = result['employee_details'].get(emp_id)
                            if emp_data_div:
                                original_div_diff = emp_data_div['kerani_differences']
                                adjustment = adjustment_distribution[div_name]
                                new_div_diff = max(0, original_div_diff + adjustment)  # Tidak boleh negatif
                                emp_data_div['kerani_differences'] = new_div_diff
                                
                                print(f"    📂 {div_name}: {original_div_diff} → {new_div_diff} ({adjustment:+d})")
                    
                    # Update total estate
                    emp_data['kerani_differences'] = target_total
                    
                else:
                    # Jika tidak ada perbedaan di divisi manapun, set ke target
                    emp_data['kerani_differences'] = target_total
                    print(f"  ✅ Set ke target: {target_total} (tidak ada perbedaan di divisi)")
            
            total_adjustment += total_adjustment_needed
    
    print(f"\n📊 HASIL AKHIR:")
    print("-" * 30)
    
    # Hitung total akhir per karyawan
    final_totals = {}
    for result in estate_results:
        div_name = result['division']
        print(f"\n📂 {div_name}:")
        for emp_id, emp_data in result['employee_details'].items():
            if emp_id not in final_totals:
                final_totals[emp_id] = 0
            final_totals[emp_id] += emp_data['kerani_differences']
            print(f"  👤 {emp_data['name']}: {emp_data['kerani_differences']} perbedaan")
    
    print(f"\n📈 TOTAL AKHIR PER KARYAWAN:")
    for emp_id, total in final_totals.items():
        target = target_differences.get(emp_id, 0)
        status = "✅ MATCH" if total == target else f"❌ SELISIH {total - target}"
        print(f"  👤 {emp_id}: {total} perbedaan {status}")
    
    print(f"\n🎯 VERIFIKASI:")
    print("-" * 30)
    
    # Verifikasi hasil
    all_match = True
    for emp_id, target in target_differences.items():
        actual = final_totals.get(emp_id, 0)
        if actual == target:
            print(f"✅ {emp_id}: {actual} = {target} (MATCH)")
        else:
            print(f"❌ {emp_id}: {actual} ≠ {target} (SELISIH {actual - target})")
            all_match = False
    
    if all_match:
        print(f"\n🎉 SEMUA TARGET TERCAPAI!")
    else:
        print(f"\n⚠️  ADA SELISIH DENGAN TARGET")
    
    return all_match

def test_edge_cases():
    """Test kasus-kasus khusus"""
    
    print(f"\n🧪 TEST KASUS KHUSUS")
    print("=" * 50)
    
    # Test 1: Satu divisi saja
    print(f"\n📋 Test 1: Satu Divisi Saja")
    estate_results = [
        {
            'division': 'Air Batu 1',
            'employee_details': {
                'ERLY': {
                    'name': 'ERLY (Mardiah)',
                    'kerani_differences': 97,
                    'total_created': 200,
                    'total_verified': 103
                }
            }
        }
    ]
    
    target_differences = {'ERLY': 71}
    
    # Hitung total awal
    estate_employee_totals = {}
    for result in estate_results:
        for emp_id, emp_data in result['employee_details'].items():
            if emp_id not in estate_employee_totals:
                estate_employee_totals[emp_id] = {
                    'name': emp_data['name'],
                    'kerani_differences': 0
                }
            estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
    
    print(f"📊 Total awal ERLY: {estate_employee_totals['ERLY']['kerani_differences']}")
    print(f"🎯 Target ERLY: {target_differences['ERLY']}")
    
    # Test 2: Tidak ada perbedaan
    print(f"\n📋 Test 2: Tidak Ada Perbedaan")
    estate_results = [
        {
            'division': 'Air Batu 1',
            'employee_details': {
                'IRWANSYAH': {
                    'name': 'IRWANSYAH (Agustina)',
                    'kerani_differences': 0,
                    'total_created': 50,
                    'total_verified': 50
                }
            }
        }
    ]
    
    target_differences = {'IRWANSYAH': 0}
    
    # Hitung total awal
    estate_employee_totals = {}
    for result in estate_results:
        for emp_id, emp_data in result['employee_details'].items():
            if emp_id not in estate_employee_totals:
                estate_employee_totals[emp_id] = {
                    'name': emp_data['name'],
                    'kerani_differences': 0
                }
            estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
    
    print(f"📊 Total awal IRWANSYAH: {estate_employee_totals['IRWANSYAH']['kerani_differences']}")
    print(f"🎯 Target IRWANSYAH: {target_differences['IRWANSYAH']}")
    
    print(f"\n✅ Test kasus khusus selesai")

if __name__ == "__main__":
    print("🚀 MULAI TEST PENYESUAIAN PROPORSIONAL")
    print("=" * 60)
    
    # Test utama
    success = test_proportional_adjustment()
    
    # Test kasus khusus
    test_edge_cases()
    
    print(f"\n🏁 TEST SELESAI")
    if success:
        print("✅ Logika penyesuaian proporsional BERHASIL")
    else:
        print("❌ Logika penyesuaian proporsional GAGAL") 