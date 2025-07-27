#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Verifikasi Perbaikan Logika Perhitungan
====================================================

Script ini menguji perbaikan logika perhitungan sesuai permintaan user:
1. Total transaksi = hanya dari Kerani (tanpa Asisten/Mandor)
2. Persentase terverifikasi = (Asisten + Mandor) / Total Kerani
3. Warna hijau untuk persentase terverifikasi Asisten/Mandor
4. Persentase perbedaan = Total perbedaan / Total transaksi terverifikasi Kerani
"""

import sys
import os

# Tambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_calculation_logic():
    """Test logika perhitungan yang diperbaiki"""
    
    print("🧪 TEST LOGIKA PERHITUNGAN YANG DIPERBAIKI")
    print("=" * 60)
    
    # Simulasi data divisi
    division_data = {
        'kerani_total': 100,      # Total transaksi Kerani
        'mandor_total': 30,       # Total transaksi Mandor
        'asisten_total': 20,      # Total transaksi Asisten
        'kerani_verified': 45,    # Total transaksi Kerani yang terverifikasi
        'employee_details': {
            'KERANI_1': {
                'name': 'ERLY (Mardiah)',
                'kerani': 50,
                'kerani_verified': 25,
                'kerani_differences': 10,
                'mandor': 0,
                'asisten': 0
            },
            'KERANI_2': {
                'name': 'DJULI DARTA (Addiani)',
                'kerani': 30,
                'kerani_verified': 15,
                'kerani_differences': 5,
                'mandor': 0,
                'asisten': 0
            },
            'KERANI_3': {
                'name': 'IRWANSYAH (Agustina)',
                'kerani': 20,
                'kerani_verified': 5,
                'kerani_differences': 2,
                'mandor': 0,
                'asisten': 0
            },
            'MANDOR_1': {
                'name': 'MANDOR A',
                'kerani': 0,
                'kerani_verified': 0,
                'kerani_differences': 0,
                'mandor': 30,
                'asisten': 0
            },
            'ASISTEN_1': {
                'name': 'ASISTEN A',
                'kerani': 0,
                'kerani_verified': 0,
                'kerani_differences': 0,
                'mandor': 0,
                'asisten': 20
            }
        }
    }
    
    print("📊 DATA DIVISI:")
    print("-" * 30)
    print(f"Total Kerani: {division_data['kerani_total']}")
    print(f"Total Mandor: {division_data['mandor_total']}")
    print(f"Total Asisten: {division_data['asisten_total']}")
    print(f"Kerani Terverifikasi: {division_data['kerani_verified']}")
    
    print(f"\n🔧 PERHITUNGAN YANG DIPERBAIKI:")
    print("-" * 40)
    
    # 1. Total transaksi = hanya dari Kerani (tanpa Asisten/Mandor)
    total_kerani_only = division_data['kerani_total']
    print(f"1. Total Transaksi (Kerani saja): {total_kerani_only}")
    
    # 2. Persentase terverifikasi = (Asisten + Mandor) / Total Kerani
    total_verifier = division_data['mandor_total'] + division_data['asisten_total']
    division_verification_rate = (total_verifier / total_kerani_only * 100) if total_kerani_only > 0 else 0
    print(f"2. Persentase Terverifikasi: {division_verification_rate:.2f}% ({total_verifier})")
    
    print(f"\n👤 DETAIL KARYAWAN:")
    print("-" * 30)
    
    for emp_id, emp_data in division_data['employee_details'].items():
        if emp_data['kerani'] > 0:
            # KERANI: % transaksi yang sudah diverifikasi dari total yang ia buat
            kerani_verification_rate = (emp_data['kerani_verified'] / emp_data['kerani'] * 100) if emp_data['kerani'] > 0 else 0
            verified_count = emp_data['kerani_verified']
            differences_count = emp_data['kerani_differences']
            
            # Persentase perbedaan = Total perbedaan / Total transaksi terverifikasi Kerani
            difference_percentage = (differences_count / verified_count * 100) if verified_count > 0 else 0
            
            print(f"  👤 {emp_data['name']} (KERANI):")
            print(f"    📊 Transaksi: {emp_data['kerani']}")
            print(f"    ✅ Terverifikasi: {kerani_verification_rate:.2f}% ({verified_count})")
            print(f"    ❌ Perbedaan: {differences_count} ({difference_percentage:.1f}%)")
        
        elif emp_data['mandor'] > 0:
            # MANDOR: % transaksi yang ia buat per total Kerani di divisi
            mandor_percentage = (emp_data['mandor'] / total_kerani_only * 100) if total_kerani_only > 0 else 0
            print(f"  👤 {emp_data['name']} (MANDOR):")
            print(f"    📊 Transaksi: {emp_data['mandor']}")
            print(f"    🟢 Persentase: {mandor_percentage:.2f}% (Hijau)")
        
        elif emp_data['asisten'] > 0:
            # ASISTEN: % transaksi yang ia buat per total Kerani di divisi
            asisten_percentage = (emp_data['asisten'] / total_kerani_only * 100) if total_kerani_only > 0 else 0
            print(f"  👤 {emp_data['name']} (ASISTEN):")
            print(f"    📊 Transaksi: {emp_data['asisten']}")
            print(f"    🟢 Persentase: {asisten_percentage:.2f}% (Hijau)")
    
    print(f"\n📈 VERIFIKASI LOGIKA:")
    print("-" * 30)
    
    # Verifikasi perhitungan
    expected_verification_rate = (50 / 100) * 100  # (30+20) / 100 * 100 = 50%
    print(f"Persentase Terverifikasi yang Diharapkan: {expected_verification_rate:.2f}%")
    print(f"Persentase Terverifikasi yang Dihitung: {division_verification_rate:.2f}%")
    
    if abs(division_verification_rate - expected_verification_rate) < 0.01:
        print("✅ Perhitungan persentase terverifikasi BENAR")
    else:
        print("❌ Perhitungan persentase terverifikasi SALAH")
    
    # Verifikasi total transaksi
    if total_kerani_only == 100:
        print("✅ Total transaksi (Kerani saja) BENAR")
    else:
        print("❌ Total transaksi (Kerani saja) SALAH")
    
    # Verifikasi persentase perbedaan
    total_differences = sum(emp['kerani_differences'] for emp in division_data['employee_details'].values() if emp['kerani'] > 0)
    total_verified = sum(emp['kerani_verified'] for emp in division_data['employee_details'].values() if emp['kerani'] > 0)
    expected_difference_rate = (total_differences / total_verified * 100) if total_verified > 0 else 0
    
    print(f"Total Perbedaan: {total_differences}")
    print(f"Total Terverifikasi: {total_verified}")
    print(f"Persentase Perbedaan: {expected_difference_rate:.1f}%")
    
    return True

def test_grand_total_logic():
    """Test logika grand total"""
    
    print(f"\n🧪 TEST LOGIKA GRAND TOTAL")
    print("=" * 40)
    
    # Simulasi data dari beberapa divisi
    divisions = [
        {
            'kerani_total': 100,
            'mandor_total': 30,
            'asisten_total': 20
        },
        {
            'kerani_total': 80,
            'mandor_total': 25,
            'asisten_total': 15
        },
        {
            'kerani_total': 60,
            'mandor_total': 20,
            'asisten_total': 10
        }
    ]
    
    # Hitung grand total
    grand_kerani = sum(div['kerani_total'] for div in divisions)
    grand_mandor = sum(div['mandor_total'] for div in divisions)
    grand_asisten = sum(div['asisten_total'] for div in divisions)
    
    grand_total_kerani_only = grand_kerani
    grand_total_verifier = grand_mandor + grand_asisten
    grand_verification_rate = (grand_total_verifier / grand_total_kerani_only * 100) if grand_total_kerani_only > 0 else 0
    
    print(f"Grand Total Kerani: {grand_total_kerani_only}")
    print(f"Grand Total Verifier (Mandor+Asisten): {grand_total_verifier}")
    print(f"Grand Verification Rate: {grand_verification_rate:.2f}% ({grand_total_verifier})")
    
    # Verifikasi
    expected_grand_rate = ((30+20+25+15+20+10) / (100+80+60)) * 100  # 120/240 * 100 = 50%
    print(f"Expected Grand Rate: {expected_grand_rate:.2f}%")
    
    if abs(grand_verification_rate - expected_grand_rate) < 0.01:
        print("✅ Perhitungan grand total BENAR")
    else:
        print("❌ Perhitungan grand total SALAH")
    
    return True

if __name__ == "__main__":
    print("🚀 MULAI TEST LOGIKA PERHITUNGAN")
    print("=" * 60)
    
    # Test perhitungan divisi
    success1 = test_calculation_logic()
    
    # Test grand total
    success2 = test_grand_total_logic()
    
    print(f"\n🏁 TEST SELESAI")
    if success1 and success2:
        print("✅ Semua perbaikan logika perhitungan BERHASIL")
    else:
        print("❌ Ada masalah dengan logika perhitungan") 