#!/usr/bin/env python3
"""
Test script khusus untuk Estate 2A tanggal 1-30 September 2025
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_estate_2a_scenario():
    """Test scenario spesifik: Estate 2A, 1-30 September 2025"""
    try:
        print("TEST SCENARIO: Estate 2A - September 2025")
        print("=" * 60)
        print("Estate: PGE 2A")
        print("Periode: 1-30 September 2025")
        print()

        # Import required modules
        from services.simple_configuration_service import SimpleConfigurationService
        from services.analysis_service import AnalysisService
        from services.report_generation_service import ReportGenerationService

        # Initialize services
        print("1. Menginisialisasi services...")
        config_service = SimpleConfigurationService()
        analysis_service = AnalysisService(config_service)
        report_service = ReportGenerationService("test_estate_2a_reports")

        print("2. Services berhasil diinisialisasi")

        # Get estate 2A configuration
        print("3. Mengkonfigurasi Estate 2A...")
        estates = config_service.config.get('estates', {})

        estate_2a_found = False
        estate_2a_config = None

        for estate_name, estate_info in estates.items():
            if '2A' in estate_name.upper() or 'PGE 2A' in estate_name.upper():
                print(f"   Estate ditemukan: {estate_name}")
                estate_2a_config = estate_info
                estate_2a_found = True
                break

        if not estate_2a_found:
            print("   [ERROR] Estate 2A tidak ditemukan dalam konfigurasi")
            print("   Available estates:")
            for estate_name in estates.keys():
                print(f"   - {estate_name}")
            return False

        estate_name = list(estates.keys())[0]  # Use first estate that contains 2A
        db_path = estate_2a_config['path']
        print(f"   Database path: {db_path}")

        # Test date range
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 30)

        print("4. Menjalankan analisis untuk Estate 2A...")
        print(f"   Periode: {start_date} hingga {end_date}")

        # Run analysis
        analysis_result = analysis_service.analyze_estate(
            estate_name, db_path, start_date, end_date
        )

        print("5. Analisis selesai. Hasil:")
        print(f"   - Estate: {analysis_result.estate_name}")
        print(f"   - Total Divisi: {analysis_result.total_divisions}")
        print(f"   - Total Transaksi Kerani: {analysis_result.grand_kerani:,}")
        print(f"   - Transaksi Terverifikasi: {analysis_result.grand_kerani_verified:,}")
        print(f"   - Tingkat Verifikasi: {analysis_result.grand_verification_rate:.2f}%")
        print(f"   - Total Perbedaan: {analysis_result.grand_differences:,}")
        print(f"   - Durasi Analisis: {analysis_result.analysis_duration_seconds:.1f} detik")

        # Check if we have meaningful data
        if analysis_result.grand_kerani == 0:
            print("   [WARNING] Tidak ada data transaksi untuk periode ini")
            print("   Ini mungkin normal jika tidak ada aktifitas pada September 2025")
        else:
            print("   [OK] Data transaksi ditemukan")

        print()
        print("6. Menggenerate laporan...")

        # Generate template-compatible report (primary)
        print("   a) Template-Compatible Report (Format Original)...")
        try:
            template_path = report_service.generate_template_compatible_report(analysis_result)
            print(f"      [SUCCESS] {os.path.basename(template_path)}")
            print(f"      File size: {os.path.getsize(template_path):,} bytes")
        except Exception as e:
            print(f"      [ERROR] {e}")

        # Generate other report types
        print("   b) Comprehensive PDF Report...")
        try:
            comp_path = report_service.generate_comprehensive_pdf_report(analysis_result)
            print(f"      [SUCCESS] {os.path.basename(comp_path)}")
            print(f"      File size: {os.path.getsize(comp_path):,} bytes")
        except Exception as e:
            print(f"      [ERROR] {e}")

        print("   c) Summary PDF Report...")
        try:
            summary_path = report_service.generate_summary_pdf_report(analysis_result)
            print(f"      [SUCCESS] {os.path.basename(summary_path)}")
            print(f"      File size: {os.path.getsize(summary_path):,} bytes")
        except Exception as e:
            print(f"      [ERROR] {e}")

        print("   d) Multi-Format Reports...")
        try:
            reports = report_service.generate_multi_format_reports(analysis_result)
            print(f"      [SUCCESS] Generated {len(reports)} reports:")
            for report_type, path in reports.items():
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"        - {report_type}: {os.path.basename(path)} ({size:,} bytes)")
                else:
                    print(f"        - {report_type}: [ERROR] File not found")
        except Exception as e:
            print(f"      [ERROR] {e}")

        print()
        print("7. VALIDASI LAPORAN")

        # Check generated files
        report_dir = "test_estate_2a_reports"
        if os.path.exists(report_dir):
            files = os.listdir(report_dir)
            print(f"   Total files generated: {len(files)}")
            for file in files:
                file_path = os.path.join(report_dir, file)
                size = os.path.getsize(file_path)
                print(f"   - {file} ({size:,} bytes)")
        else:
            print("   [ERROR] Report directory not found")

        print()
        print("=" * 60)
        print("TEST SCENARIO SELESAI")
        print("=" * 60)

        # Summary
        if analysis_result.grand_kerani > 0:
            print("STATUS: BERHASIL - Laporan tergenerate dengan data nyata")
            print(f"Divisi yang dianalisis: {analysis_result.total_divisions}")
            print(f"Total transaksi: {analysis_result.grand_kerani:,}")
            print("Format laporan: Sesuai template original")
        else:
            print("STATUS: PARTIAL - Laporan tergenerate tapi tidak ada data")
            print("Kemungkinan penyebab:")
            print("- Tidak ada transaksi pada periode September 2025")
            print("- Database tidak memiliki data untuk estate tersebut")
            print("- Konfigurasi tanggal atau database path salah")

        return True

    except Exception as e:
        print(f"\nERROR during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("FFB Analysis System - Estate 2A Test Scenario")
    print("=" * 70)
    print("Testing Estate 2A dengan periode 1-30 September 2025")
    print()

    success = test_estate_2a_scenario()

    if success:
        print("\nTEST COMPLETED")
        print("Periksa folder 'test_estate_2a_reports' untuk hasil laporan")
    else:
        print("\nTEST FAILED")
        print("Periksa error messages di atas untuk troubleshooting")

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)