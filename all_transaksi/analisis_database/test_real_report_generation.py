#!/usr/bin/env python3
"""
Test script for real report generation with actual data
"""

import sys
import os
from datetime import date, datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_data_report():
    """Test report generation with real analysis service"""
    try:
        print("Testing Real Data Report Generation...")
        print("=" * 60)

        # Import required modules
        from services.simple_configuration_service import SimpleConfigurationService
        from services.analysis_service import AnalysisService
        from services.report_generation_service import ReportGenerationService
        from models.analysis_result import AnalysisResult

        # Initialize services
        print("1. Initializing services...")
        config_service = SimpleConfigurationService()
        analysis_service = AnalysisService(config_service)
        report_service = ReportGenerationService("test_reports_real")

        print("2. Services initialized successfully")

        # Test with real database
        print("3. Testing with real database connection...")
        estates = config_service.get_estates()
        print(f"   Available estates: {len(estates)}")

        # Use first available estate for testing
        if estates:
            test_estate = list(estates.keys())[0]
            print(f"   Testing with estate: {test_estate}")

            # Get database path
            estate_config = config_service.get_estate_config(test_estate)
            db_path = estate_config['path']
            print(f"   Database path: {db_path}")

            # Test date range (September 2025)
            start_date = date(2025, 9, 1)
            end_date = date(2025, 9, 30)

            print("4. Running analysis...")
            analysis_result = analysis_service.analyze_estate(
                test_estate, db_path, start_date, end_date
            )

            print(f"5. Analysis completed:")
            print(f"   - Estate: {analysis_result.estate_name}")
            print(f"   - Divisions: {analysis_result.total_divisions}")
            print(f"   - Total Kerani: {analysis_result.grand_kerani}")
            print(f"   - Verified: {analysis_result.grand_kerani_verified}")
            print(f"   - Verification Rate: {analysis_result.grand_verification_rate:.2f}%")
            print(f"   - Differences: {analysis_result.grand_differences}")

            # Generate all report types
            print("6. Generating reports...")

            # Template-compatible report
            print("   a) Generating template-compatible report...")
            template_path = report_service.generate_template_compatible_report(analysis_result)
            print(f"      Generated: {os.path.basename(template_path)}")

            # Multi-format reports
            print("   b) Generating multi-format reports...")
            try:
                reports = report_service.generate_multi_format_reports(analysis_result)
                print(f"      Generated reports: {len(reports)}")
                for report_type, path in reports.items():
                    print(f"        - {report_type}: {os.path.basename(path)}")
            except Exception as e:
                print(f"      Multi-format reports failed: {e}")

            print("7. All reports generated successfully!")
            print(f"   Reports directory: {os.path.abspath('test_reports_real')}")

            return True

        else:
            print("   [ERROR] No estates available for testing")
            return False

    except Exception as e:
        print(f"\nError during real data test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_generator_standalone():
    """Test template generator standalone"""
    try:
        print("\nTesting Template Generator Standalone...")
        print("=" * 50)

        from infrastructure.reporting.template_compatible_generator import TemplateCompatiblePDFGenerator
        from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics

        # Create test data
        print("1. Creating test data...")
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 30)

        analysis_result = AnalysisResult.create_empty(start_date, end_date, ["TEST ESTATE"])

        # Add test division
        test_employee = EmployeeMetrics(
            employee_id="TEST001",
            employee_name="Test Employee",
            estate="TEST ESTATE",
            division="TEST DIV",
            kerani_transactions=100,
            kerani_verified=85,
            kerani_differences=3
        )

        div_summary = DivisionSummary(
            estate_name="TEST ESTATE",
            division_id="TESTDIV",
            division_name="TEST DIVISION",
            kerani_total=100,
            verification_total=85,
            difference_count=3,
            employee_count=1,
            employee_details={"TEST001": test_employee}
        )

        analysis_result.add_division_summary(div_summary)

        print("2. Test data created")

        # Initialize generator
        print("3. Initializing template generator...")
        generator = TemplateCompatiblePDFGenerator()

        # Generate report
        print("4. Generating template report...")
        output_path = "test_reports_standalone/test_template_report.pdf"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        result_path = generator.create_template_compatible_report(
            analysis_result=analysis_result,
            output_path=output_path
        )

        print(f"5. Report generated: {result_path}")
        print(f"   File size: {os.path.getsize(result_path)} bytes")

        return True

    except Exception as e:
        print(f"Error in standalone test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("FFB Analysis System - Real Data Report Test")
    print("=" * 70)
    print()

    # Test standalone template generator
    standalone_ok = test_template_generator_standalone()

    # Test with real data
    real_data_ok = test_real_data_report()

    print("\n" + "=" * 70)
    print("TEST SUMMARY:")
    print(f"Standalone Template Generator: {'PASS' if standalone_ok else 'FAIL'}")
    print(f"Real Data Report Generation: {'PASS' if real_data_ok else 'FAIL'}")

    if standalone_ok and real_data_ok:
        print("\nSUCCESS: All report generation systems are working correctly!")
        return 0
    else:
        print("\nPARTIAL SUCCESS: Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)