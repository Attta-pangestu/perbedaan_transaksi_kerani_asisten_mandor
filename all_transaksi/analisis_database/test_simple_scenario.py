#!/usr/bin/env python3
"""
Test script sederhana untuk Estate 2A - September 2025
"""

import sys
import os
from datetime import date, datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_scenario():
    """Test sederhana dengan data mock untuk Estate 2A"""
    try:
        print("TEST SEDERHANA: Estate 2A Scenario")
        print("=" * 50)
        print("Estate: PGE 2A")
        print("Periode: 1-30 September 2025")
        print()

        # Import required modules
        from services.report_generation_service import ReportGenerationService
        from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics

        print("1. Membuat data test untuk Estate 2A...")

        # Create mock analysis result yang realistis untuk Estate 2A
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 30)

        analysis_result = AnalysisResult.create_empty(start_date, end_date, ["PGE 2A"])
        analysis_result.analysis_duration_seconds = 8.5

        # Create realistic employee data for Estate 2A
        employees_data = [
            # Division 1 - Block A
            EmployeeMetrics(
                employee_id="E001", employee_name="Ahmad Susanto", estate="PGE 2A", division="DIV-01",
                kerani_transactions=450, kerani_verified=380, kerani_differences=8
            ),
            EmployeeMetrics(
                employee_id="E002", employee_name="Budi Santoso", estate="PGE 2A", division="DIV-01",
                kerani_transactions=380, kerani_verified=320, kerani_differences=5
            ),
            EmployeeMetrics(
                employee_id="M001", employee_name="Chandra Wijaya", estate="PGE 2A", division="DIV-01",
                mandor_transactions=350
            ),
            EmployeeMetrics(
                employee_id="A001", employee_name="Dedi Kurniawan", estate="PGE 2A", division="DIV-01",
                asisten_transactions=280
            ),

            # Division 2 - Block B
            EmployeeMetrics(
                employee_id="E003", employee_name="Eko Prasetyo", estate="PGE 2A", division="DIV-02",
                kerani_transactions=520, kerani_verified=445, kerani_differences=12
            ),
            EmployeeMetrics(
                employee_id="E004", employee_name="Fajar Hidayat", estate="PGE 2A", division="DIV-02",
                kerani_transactions=410, kerani_verified=395, kerani_differences=3
            ),
            EmployeeMetrics(
                employee_id="M002", employee_name="Gunawan Subagyo", estate="PGE 2A", division="DIV-02",
                mandor_transactions=420
            ),

            # Division 3 - Block C
            EmployeeMetrics(
                employee_id="E005", employee_name="Hendra Wijaya", estate="PGE 2A", division="DIV-03",
                kerani_transactions=390, kerani_verified=310, kerani_differences=15
            ),
            EmployeeMetrics(
                employee_id="E006", employee_name="Indra Lesmana", estate="PGE 2A", division="DIV-03",
                kerani_transactions=360, kerani_verified=340, kerani_differences=2
            ),
            EmployeeMetrics(
                employee_id="M003", employee_name="Joko Sutrisno", estate="PGE 2A", division="DIV-03",
                mandor_transactions=380
            ),
            EmployeeMetrics(
                employee_id="A002", employee_name="Kartono Sutomo", estate="PGE 2A", division="DIV-03",
                asisten_transactions=320
            ),
        ]

        # Create division summaries
        divisions = {
            "DIV-01": {"employees": [], "kerani_total": 0, "verified_total": 0, "differences": 0},
            "DIV-02": {"employees": [], "kerani_total": 0, "verified_total": 0, "differences": 0},
            "DIV-03": {"employees": [], "kerani_total": 0, "verified_total": 0, "differences": 0},
        }

        for emp in employees_data:
            divisions[emp.division]["employees"].append(emp)
            if emp.kerani_transactions > 0:
                divisions[emp.division]["kerani_total"] += emp.kerani_transactions
                divisions[emp.division]["verified_total"] += emp.kerani_verified
                divisions[emp.division]["differences"] += emp.kerani_differences

        # Add divisions to analysis result
        for div_id, div_data in divisions.items():
            employee_details = {emp.employee_id: emp for emp in div_data["employees"]}

            div_summary = DivisionSummary(
                estate_name="PGE 2A",
                division_id=div_id,
                division_name=f"Division {div_id.split('-')[1]} - Block {chr(65 + int(div_id.split('-')[1]) - 1)}",
                kerani_total=div_data["kerani_total"],
                verification_total=div_data["verified_total"],
                difference_count=div_data["differences"],
                employee_count=len(div_data["employees"]),
                employee_details=employee_details
            )

            analysis_result.add_division_summary(div_summary)

        print("2. Data test berhasil dibuat:")
        print(f"   - Total Divisions: {analysis_result.total_divisions}")
        print(f"   - Total Kerani Transactions: {analysis_result.grand_kerani:,}")
        print(f"   - Total Verified: {analysis_result.grand_kerani_verified:,}")
        print(f"   - Verification Rate: {analysis_result.grand_verification_rate:.2f}%")
        print(f"   - Total Differences: {analysis_result.grand_differences:,}")

        print()
        print("3. Menggenerate laporan...")

        # Initialize report service
        report_service = ReportGenerationService("test_estate_2a_mock")

        # Generate template-compatible report
        print("   a) Template-Compatible Report (Format Original)...")
        try:
            template_path = report_service.generate_template_compatible_report(analysis_result)
            print(f"      [SUCCESS] {os.path.basename(template_path)}")
            print(f"      File size: {os.path.getsize(template_path):,} bytes")
            print(f"      Full path: {template_path}")
        except Exception as e:
            print(f"      [ERROR] {e}")
            import traceback
            traceback.print_exc()

        # Generate comprehensive report
        print("   b) Comprehensive PDF Report...")
        try:
            comp_path = report_service.generate_comprehensive_pdf_report(analysis_result)
            print(f"      [SUCCESS] {os.path.basename(comp_path)}")
            print(f"      File size: {os.path.getsize(comp_path):,} bytes")
        except Exception as e:
            print(f"      [ERROR] {e}")

        # Generate summary report
        print("   c) Summary PDF Report...")
        try:
            summary_path = report_service.generate_summary_pdf_report(analysis_result)
            print(f"      [SUCCESS] {os.path.basename(summary_path)}")
            print(f"      File size: {os.path.getsize(summary_path):,} bytes")
        except Exception as e:
            print(f"      [ERROR] {e}")

        # Generate multi-format reports
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
        print("4. VALIDASI FILE")

        report_dir = "test_estate_2a_mock"
        if os.path.exists(report_dir):
            files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
            print(f"   PDF files generated: {len(files)}")

            for file in files:
                file_path = os.path.join(report_dir, file)
                size = os.path.getsize(file_path)
                print(f"   - {file} ({size:,} bytes)")

                # Validasi file size yang reasonable
                if size > 1000:  # At least 1KB
                    print(f"     Status: [OK] File size reasonable")
                else:
                    print(f"     Status: [WARNING] File too small")

        print()
        print("=" * 50)
        print("TEST SELESAI")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("FFB Analysis System - Simple Estate 2A Test")
    print("=" * 60)
    print("Mock data untuk Estate 2A - September 2025")
    print()

    success = test_simple_scenario()

    if success:
        print("\n[SUCCESS] Test berhasil diselesaikan!")
        print("Laporan telah digenerate dengan format yang sesuai template original.")
        print("Periksa folder 'test_estate_2a_mock' untuk hasil laporan PDF.")
    else:
        print("\n[FAILED] Test gagal!")
        print("Periksa error messages di atas.")

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)