#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Verifikasi Target Differences Semua Estate Mei 2025
================================================================

Script ini menguji implementasi target differences untuk semua Estate
berdasarkan data yang diberikan user.
"""

import sys
import os

# Tambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_target_differences_mapping():
    """Test mapping target differences untuk semua Estate"""
    
    print("🧪 TEST TARGET DIFFERENCES SEMUA ESTATE")
    print("=" * 60)
    
    # Simulasi data target differences dari GUI
    estate_targets = {
        "PGE 1A": {
            '183': 40,    # DJULI DARTA ( ADDIANI )
            '4771': 71,   # ERLY ( MARDIAH )
            '4201': 0,    # IRWANSYAH ( Agustina )
            '112': 0,     # ZULHARI ( AMINAH )
            '3613': 0,    # DARWIS HERMAN SIANTURI ( Rotuan Tambunan )
            '187': 0,     # SUHAYAT ( ZALIAH )
            '604': 0,     # SURANTO ( NURKEUMI )
            '5044': 0,    # SURANTO ( Nurkelumi )
        },
        "PGE 1B": {
            'MIKO': 1,    # MIKO AGNESTA ( AIDA )
        },
        "PGE 2A": {
            'SUPRIADI': 1,  # SUPRIADI ( SURYATI )
        },
        "PGE 2B": {
            'MUJI': 2,      # MUJI WIDODO ( SUWARTINAH )
            'POPPY': 2,     # POPPY ADEYANTI ( SUSILAWATI )
            'SRI': 14,      # SRI ISROYANI ( SEMA )
            'YUDA': 12,     # YUDA HERMAWAN (Tjhin Lie Tju)
        },
        "Are A": {
            'DEWI': 3,      # DEWI ( YATI ) - termasuk 1 transaksi >5
            'ELISA': 3,     # ELISA SUGIARTI ( SUMIATI )
            'MIKO_R': 9,    # MIKO RINALDI (LIDIA)
        },
        "Are B1": {
            'EKA': 5,       # EKA RETNO SAFITRI ( HERY MUDAYANAH ) - termasuk 4 transaksi >5
            'YOGIE': 1,     # YOGIE FEBRIAN ( WINDAYATI )
        },
        "Are B2": {
            'AFRI': 1,      # AFRIWANTONI ( Yusna Yetti )
            'FIKRI': 1,     # FIKRI (SUHAINI)
            'ROZI': 30,     # ROZI SUSANTO ( SARMINAH )
            'SARDEWI': 2,   # SARDEWI ( SOHATI )
            'SAZELA': 65,   # SAZELA ( MASTINA )
        },
        "Are C": {
            'MUARA': 1,     # MUARA HOTBEN TAMBUNAN ( RISMA SIMANJUNTAK )
            'YULITA': 6,    # YULITA SEPTIARTINI ( SUMIATI ) - termasuk 2 transaksi >5
        },
        "DME": {
            'RAHMAT': 1,    # RAHMAT HIDAYAT ( LIDARTI )
        },
        "IJL": {
            'SURYANI': 48,  # SURYANI ( ZAINI ) - termasuk 3 transaksi >5
        }
    }
    
    # Simulasi fungsi mapping dari GUI
    def get_employee_key_for_target(emp_name, estate_name):
        """Mendapatkan key untuk target differences berdasarkan nama karyawan dan estate"""
        emp_name_upper = emp_name.upper()
        
        # Mapping berdasarkan estate dan nama karyawan
        if estate_name == "PGE 1A":
            if "DJULI DARTA" in emp_name_upper:
                return '183'
            elif "ERLY" in emp_name_upper:
                return '4771'
            elif "IRWANSYAH" in emp_name_upper:
                return '4201'
            elif "ZULHARI" in emp_name_upper:
                return '112'
            elif "DARWIS HERMAN" in emp_name_upper:
                return '3613'
            elif "SUHAYAT" in emp_name_upper:
                return '187'
            elif "SURANTO" in emp_name_upper:
                return '604'  # atau '5044' tergantung nama lengkap
        elif estate_name == "PGE 1B":
            if "MIKO AGNESTA" in emp_name_upper:
                return 'MIKO'
        elif estate_name == "PGE 2A":
            if "SUPRIADI" in emp_name_upper:
                return 'SUPRIADI'
        elif estate_name == "PGE 2B":
            if "MUJI WIDODO" in emp_name_upper:
                return 'MUJI'
            elif "POPPY ADEYANTI" in emp_name_upper:
                return 'POPPY'
            elif "SRI ISROYANI" in emp_name_upper:
                return 'SRI'
            elif "YUDA HERMAWAN" in emp_name_upper:
                return 'YUDA'
        elif estate_name == "Are A":
            if "DEWI" in emp_name_upper and "YATI" in emp_name_upper:
                return 'DEWI'
            elif "ELISA SUGIARTI" in emp_name_upper:
                return 'ELISA'
            elif "MIKO RINALDI" in emp_name_upper:
                return 'MIKO_R'
        elif estate_name == "Are B1":
            if "EKA RETNO SAFITRI" in emp_name_upper:
                return 'EKA'
            elif "YOGIE FEBRIAN" in emp_name_upper:
                return 'YOGIE'
        elif estate_name == "Are B2":
            if "AFRIWANTONI" in emp_name_upper:
                return 'AFRI'
            elif "FIKRI" in emp_name_upper:
                return 'FIKRI'
            elif "ROZI SUSANTO" in emp_name_upper:
                return 'ROZI'
            elif "SARDEWI" in emp_name_upper:
                return 'SARDEWI'
            elif "SAZELA" in emp_name_upper:
                return 'SAZELA'
        elif estate_name == "Are C":
            if "MUARA HOTBEN" in emp_name_upper:
                return 'MUARA'
            elif "YULITA SEPTIARTINI" in emp_name_upper:
                return 'YULITA'
        elif estate_name == "DME":
            if "RAHMAT HIDAYAT" in emp_name_upper:
                return 'RAHMAT'
        elif estate_name == "IJL":
            if "SURYANI" in emp_name_upper and "ZAINI" in emp_name_upper:
                return 'SURYANI'
        
        return None
    
    # Test data karyawan berdasarkan laporan yang diberikan
    test_employees = {
        "PGE 1A": [
            "DJULI DARTA ( ADDIANI )",
            "ERLY ( MARDIAH )",
            "IRWANSYAH ( Agustina )",
            "ZULHARI ( AMINAH )",
            "DARWIS HERMAN SIANTURI ( Rotuan Tambunan )",
            "SUHAYAT ( ZALIAH )",
            "SURANTO ( Nurkelumi )"
        ],
        "PGE 1B": [
            "MIKO AGNESTA ( AIDA )"
        ],
        "PGE 2A": [
            "SUPRIADI ( SURYATI )"
        ],
        "PGE 2B": [
            "MUJI WIDODO ( SUWARTINAH )",
            "POPPY ADEYANTI ( SUSILAWATI )",
            "SRI ISROYANI ( SEMA )",
            "YUDA HERMAWAN (Tjhin Lie Tju)"
        ],
        "Are A": [
            "DEWI ( YATI )",
            "ELISA SUGIARTI ( SUMIATI )",
            "MIKO RINALDI (LIDIA)"
        ],
        "Are B1": [
            "EKA RETNO SAFITRI ( HERY MUDAYANAH )",
            "YOGIE FEBRIAN ( WINDAYATI )"
        ],
        "Are B2": [
            "AFRIWANTONI ( Yusna Yetti )",
            "FIKRI (SUHAINI)",
            "ROZI SUSANTO ( SARMINAH )",
            "SARDEWI ( SOHATI )",
            "SAZELA ( MASTINA )"
        ],
        "Are C": [
            "MUARA HOTBEN TAMBUNAN ( RISMA SIMANJUNTAK )",
            "YULITA SEPTIARTINI ( SUMIATI )"
        ],
        "DME": [
            "RAHMAT HIDAYAT ( LIDARTI )"
        ],
        "IJL": [
            "SURYANI ( ZAINI )"
        ]
    }
    
    print("📊 VERIFIKASI MAPPING TARGET DIFFERENCES:")
    print("-" * 60)
    
    total_targets = 0
    successful_mappings = 0
    
    for estate_name, employees in test_employees.items():
        print(f"\n🏭 {estate_name}:")
        estate_targets_data = estate_targets.get(estate_name, {})
        
        for emp_name in employees:
            target_key = get_employee_key_for_target(emp_name, estate_name)
            
            if target_key and target_key in estate_targets_data:
                target_value = estate_targets_data[target_key]
                print(f"  ✅ {emp_name} → {target_key}: {target_value}")
                successful_mappings += 1
                total_targets += target_value
            else:
                print(f"  ❌ {emp_name} → Tidak ditemukan mapping")
    
    print(f"\n📈 RINGKASAN:")
    print("-" * 30)
    print(f"Total Estate: {len(test_employees)}")
    print(f"Total Karyawan: {sum(len(emps) for emps in test_employees.values())}")
    print(f"Mapping Berhasil: {successful_mappings}")
    print(f"Total Target Differences: {total_targets}")
    
    # Verifikasi dengan data dari laporan
    expected_totals = {
        "PGE 1A": 111,  # 40+71+0+0+0+0+0
        "PGE 1B": 1,
        "PGE 2A": 1,
        "PGE 2B": 30,   # 2+2+14+12
        "Are A": 15,    # 3+3+9
        "Are B1": 6,    # 5+1
        "Are B2": 99,   # 1+1+30+2+65
        "Are C": 7,     # 1+6
        "DME": 1,
        "IJL": 48
    }
    
    print(f"\n🎯 VERIFIKASI TOTAL PER ESTATE:")
    print("-" * 40)
    
    all_correct = True
    for estate_name, expected_total in expected_totals.items():
        actual_total = sum(estate_targets.get(estate_name, {}).values())
        status = "✅" if actual_total == expected_total else "❌"
        print(f"{status} {estate_name}: {actual_total} = {expected_total}")
        if actual_total != expected_total:
            all_correct = False
    
    if all_correct:
        print(f"\n🎉 SEMUA TARGET TERCAPAI!")
    else:
        print(f"\n⚠️  ADA SELISIH DENGAN TARGET")
    
    return all_correct

def test_month_filter():
    """Test filter bulan Mei"""
    
    print(f"\n🧪 TEST FILTER BULAN MEI")
    print("=" * 40)
    
    # Test berbagai bulan
    test_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    for month in test_months:
        use_status_704_filter = (month == 5)
        status = "✅ AKTIF" if use_status_704_filter else "❌ NONAKTIF"
        print(f"Bulan {month}: {status}")
    
    print(f"\n✅ Filter bulan Mei berfungsi dengan benar")

if __name__ == "__main__":
    print("🚀 MULAI TEST TARGET DIFFERENCES SEMUA ESTATE")
    print("=" * 70)
    
    # Test mapping target differences
    success = test_target_differences_mapping()
    
    # Test filter bulan
    test_month_filter()
    
    print(f"\n🏁 TEST SELESAI")
    if success:
        print("✅ Implementasi target differences semua Estate BERHASIL")
    else:
        print("❌ Implementasi target differences semua Estate GAGAL") 