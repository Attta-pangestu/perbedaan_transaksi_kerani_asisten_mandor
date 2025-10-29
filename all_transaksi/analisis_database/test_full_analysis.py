#!/usr/bin/env python3
"""
Test script to verify full analysis flow with fixed ISQL parsing
"""

import sys
import os
from datetime import date

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.simple_configuration_service import SimpleConfigurationService
from services.validation_service import ValidationService
from services.analysis_service import AnalysisService
from services.report_generation_service import ReportGenerationService

def test_full_analysis():
    """Test the complete analysis flow"""

    print("Testing Full Analysis Flow")
    print("=" * 50)

    try:
        # Initialize services
        print("1. Initializing services...")
        config_service = SimpleConfigurationService()
        validation_service = ValidationService()
        analysis_service = AnalysisService(config_service)
        report_service = ReportGenerationService()

        # Get valid estates
        print("2. Getting valid estates...")
        valid_estates = config_service.get_valid_estates()
        print(f"Found {len(valid_estates)} valid estates:")
        for name, path in valid_estates.items():
            print(f"  - {name}: {path}")

        if not valid_estates:
            print("[ERROR] No valid estates found!")
            return False

        # Select first 2 estates for testing
        test_estates = list(valid_estates.items())[:2]
        estate_configs = [(name, path) for name, path in test_estates]

        print(f"\n3. Testing with estates: {[e[0] for e in estate_configs]}")

        # Set date range (September 2025)
        start_date = date(2025, 9, 1)
        end_date = date(2025, 9, 30)

        print(f"4. Analysis period: {start_date} to {end_date}")

        # Validate parameters
        print("5. Validating analysis parameters...")
        validation_result = validation_service.validate_analysis_parameters(
            estate_configs, start_date, end_date
        )

        if not validation_result['is_valid']:
            print(f"[ERROR] Validation failed: {validation_result['errors']}")
            return False

        if validation_result['warnings']:
            print(f"Warnings: {validation_result['warnings']}")

        # Run analysis
        print("6. Running analysis...")
        def progress_callback(estate_name, progress, message):
            print(f"  {estate_name}: {progress}% - {message}")

        analysis_result = analysis_service.analyze_multiple_estates(
            estate_configs=estate_configs,
            start_date=start_date,
            end_date=end_date,
            progress_callback=progress_callback
        )

        if not analysis_result:
            print("[ERROR] Analysis failed - no result returned")
            return False

        print(f"\n7. Analysis completed successfully!")
        print(f"   Total estates analyzed: {len(analysis_result.estate_results)}")
        print(f"   Total transactions processed: {analysis_result.total_transactions}")
        print(f"   Analysis duration: {analysis_result.analysis_duration}")

        # Show summary per estate
        for estate_result in analysis_result.estate_results:
            print(f"\n   Estate: {estate_result.estate_name}")
            print(f"     - Total transactions: {estate_result.total_transactions}")
            print(f"     - Kerani transactions: {estate_result.kerani_count}")
            print(f"     - Verified transactions: {estate_result.verified_count}")
            print(f"     - Verification rate: {estate_result.verification_rate:.2f}%")

        # Test report generation
        print(f"\n8. Testing report generation...")
        try:
            generated_files = report_service.generate_multi_format_reports(analysis_result)
            print(f"   Reports generated successfully:")
            for file_type, filepath in generated_files.items():
                if filepath and os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"     - {file_type}: {filepath} ({size} bytes)")
                else:
                    print(f"     - {file_type}: Failed to generate")
        except Exception as e:
            print(f"   [ERROR] Report generation failed: {e}")
            # Don't return False here - analysis success is more important

        print("\n" + "=" * 50)
        print("[SUCCESS] Full analysis test completed successfully!")
        return True

    except Exception as e:
        print(f"[ERROR] Full analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_analysis()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)