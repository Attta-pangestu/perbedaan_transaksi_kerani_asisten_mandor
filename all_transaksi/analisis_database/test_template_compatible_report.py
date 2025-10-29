#!/usr/bin/env python3
"""
Test script for template-compatible report generation
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_template_compatible_report():
    """Test the template-compatible report generation"""
    try:
        print("Testing Template-Compatible Report Generation...")
        print("=" * 60)

        # Import required modules
        from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics
        from services.report_generation_service import ReportGenerationService

        # Create test data
        print("1. Creating test data...")
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 30)
        estate_name = "PGE 1A"

        # Create test analysis result
        analysis_result = AnalysisResult.create_empty(start_date, end_date, [estate_name])
        analysis_result.analysis_duration_seconds = 120.5
        analysis_result.use_status_704_filter = True

        # Create test employees
        test_employees = [
            EmployeeMetrics(
                employee_id="EMP001",
                employee_name="John Doe",
                estate=estate_name,
                division="DIV001",
                kerani_transactions=100,
                kerani_verified=85,
                kerani_differences=5,
                mandor_transactions=0,
                asisten_transactions=0
            ),
            EmployeeMetrics(
                employee_id="EMP002",
                employee_name="Jane Smith",
                estate=estate_name,
                division="DIV001",
                kerani_transactions=0,
                kerani_verified=0,
                kerani_differences=0,
                mandor_transactions=75,
                asisten_transactions=0
            ),
            EmployeeMetrics(
                employee_id="EMP003",
                employee_name="Bob Johnson",
                estate=estate_name,
                division="DIV001",
                kerani_transactions=0,
                kerani_verified=0,
                kerani_differences=0,
                mandor_transactions=0,
                asisten_transactions=60
            ),
            EmployeeMetrics(
                employee_id="EMP004",
                employee_name="Alice Brown",
                estate=estate_name,
                division="DIV002",
                kerani_transactions=120,
                kerani_verified=95,
                kerani_differences=8,
                mandor_transactions=0,
                asisten_transactions=0
            )
        ]

        # Create division summaries
        div1_summary = DivisionSummary(
            estate_name=estate_name,
            division_id="DIV001",
            division_name="DIVISION 1",
            kerani_total=100,
            mandor_total=75,
            asisten_total=60,
            verification_total=85,
            difference_count=5,
            employee_count=3,
            employee_details={emp.employee_id: emp for emp in test_employees[:3]}
        )

        div2_summary = DivisionSummary(
            estate_name=estate_name,
            division_id="DIV002",
            division_name="DIVISION 2",
            kerani_total=120,
            mandor_total=0,
            asisten_total=0,
            verification_total=95,
            difference_count=8,
            employee_count=1,
            employee_details={test_employees[3].employee_id: test_employees[3]}
        )

        # Add divisions to analysis result
        analysis_result.add_division_summary(div1_summary)
        analysis_result.add_division_summary(div2_summary)

        print("2. Test data created successfully")
        print(f"   - Estates: {analysis_result.analyzed_estates}")
        print(f"   - Divisions: {analysis_result.total_divisions}")
        print(f"   - Total Employees: {len(analysis_result.employee_metrics)}")
        print(f"   - Grand Kerani: {analysis_result.grand_kerani}")
        print(f"   - Grand Verified: {analysis_result.grand_kerani_verified}")
        print(f"   - Grand Verification Rate: {analysis_result.grand_verification_rate:.2f}%")

        # Initialize report service
        print("3. Initializing report generation service...")
        report_service = ReportGenerationService("test_reports")

        # Generate template-compatible report
        print("4. Generating template-compatible PDF report...")
        report_path = report_service.generate_template_compatible_report(analysis_result)

        print(f"5. Report generated successfully: {report_path}")
        print(f"   File size: {os.path.getsize(report_path)} bytes")

        # Check if file exists and is readable
        if os.path.exists(report_path):
            print("6. [OK] Report file created and accessible")
            print(f"   - Full path: {os.path.abspath(report_path)}")
        else:
            print("6. [ERROR] Report file not found!")
            return False

        print("\n" + "=" * 60)
        print("Template-Compatible Report Generation Test: SUCCESS")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_loading():
    """Test if template file can be loaded"""
    try:
        print("Testing Template Loading...")
        print("=" * 40)

        template_path = "template_laporan/verifikasi_transaksi_mandor_kerani_asisten/template_exact_match.json"

        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                import json
                template_data = json.load(f)

            print("[OK] Template loaded successfully")
            print(f"  - Template name: {template_data.get('ffb_verification_report_template', {}).get('name', 'Unknown')}")
            print(f"  - Version: {template_data.get('ffb_verification_report_template', {}).get('version', 'Unknown')}")
            return True
        else:
            print(f"[ERROR] Template file not found: {template_path}")
            return False

    except Exception as e:
        print(f"Error loading template: {e}")
        return False

def main():
    """Main test function"""
    print("FFB Analysis System - Template-Compatible Report Test")
    print("=" * 70)
    print()

    # Test template loading
    template_ok = test_template_loading()
    print()

    # Test report generation
    report_ok = test_template_compatible_report()
    print()

    if template_ok and report_ok:
        print("SUCCESS: All tests passed! Template-compatible system is working correctly.")
        return 0
    else:
        print("ERROR: Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)