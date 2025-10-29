#!/usr/bin/env python3
"""
Test Runner untuk FFB Analysis System

Script untuk menjalankan semua test suite dan generate test reports
"""

import sys
import os
import unittest
import time
from pathlib import Path
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_all_tests(verbosity=2, generate_report=False):
    """
    Run all test suites

    Args:
        verbosity: Test verbosity level
        generate_report: Whether to generate HTML test report

    Returns:
        Test result object
    """
    print("=" * 70)
    print("FFB Analysis System - Test Suite Runner")
    print("=" * 70)

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Create test runner
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True
    )

    # Run tests
    print(f"Discovering tests in: {start_dir}")
    print(f"Running tests with verbosity level: {verbosity}")
    print("-" * 70)

    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Time elapsed: {end_time - start_time:.2f} seconds")

    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")

    # Success status
    was_successful = result.wasSuccessful()
    print(f"\nOverall result: {'SUCCESS' if was_successful else 'FAILED'}")

    # Generate report if requested
    if generate_report:
        generate_test_report(result, end_time - start_time)

    return result

def generate_test_report(result, elapsed_time):
    """
    Generate HTML test report

    Args:
        result: Test result object
        elapsed_time: Total test execution time
    """
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.html"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>FFB Analysis System - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #2E4053; color: white; padding: 20px; text-align: center; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .failure {{ color: #dc3545; font-weight: bold; }}
        .error {{ color: #fd7e14; font-weight: bold; }}
        .test-section {{ margin: 20px 0; }}
        .test-case {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
        pre {{ background-color: #f8f9fa; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>FFB Analysis System - Test Report</h1>
        <p>Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="summary">
        <h2>Test Summary</h2>
        <p><strong>Tests Run:</strong> {result.testsRun}</p>
        <p><strong>Failures:</strong> <span class="failure">{len(result.failures)}</span></p>
        <p><strong>Errors:</strong> <span class="error">{len(result.errors)}</span></p>
        <p><strong>Time Elapsed:</strong> {elapsed_time:.2f} seconds</p>
        <p><strong>Result:</strong> <span class="{'success' if result.wasSuccessful() else 'failure'}">
            {'SUCCESS' if result.wasSuccessful() else 'FAILED'}
        </span></p>
    </div>

    <div class="test-section">
        <h2>Failed Tests</h2>
"""

        if result.failures:
            for test, traceback in result.failures:
                html_content += f"""
        <div class="test-case">
            <h3 class="failure">{test}</h3>
            <pre>{traceback}</pre>
        </div>
"""
        else:
            html_content += "<p>No failed tests!</p>"

        html_content += """
    </div>

    <div class="test-section">
        <h2>Error Tests</h2>
"""

        if result.errors:
            for test, traceback in result.errors:
                html_content += f"""
        <div class="test-case">
            <h3 class="error">{test}</h3>
            <pre>{traceback}</pre>
        </div>
"""
        else:
            html_content += "<p>No test errors!</p>"

        html_content += """
    </div>
</body>
</html>
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\nHTML report generated: {report_file}")

    except Exception as e:
        print(f"Error generating HTML report: {e}")

def run_specific_test_module(module_name, verbosity=2):
    """
    Run specific test module

    Args:
        module_name: Name of test module (e.g., 'test_database')
        verbosity: Test verbosity level
    """
    print(f"Running specific test module: {module_name}")

    try:
        # Import the test module
        test_module = __import__(f'tests.{module_name}', fromlist=[''])

        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)

        # Run tests
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)

        return result

    except ImportError as e:
        print(f"Error importing test module {module_name}: {e}")
        return None

def main():
    """
    Main function to run tests
    """
    parser = argparse.ArgumentParser(description='FFB Analysis System Test Runner')
    parser.add_argument(
        '--module', '-m',
        help='Run specific test module (e.g., test_database, test_analysis)'
    )
    parser.add_argument(
        '--verbosity', '-v',
        type=int,
        default=2,
        choices=[0, 1, 2],
        help='Test verbosity level (0=quiet, 1=normal, 2=detailed)'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate HTML test report'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available test modules'
    )

    args = parser.parse_args()

    if args.list:
        # List available test modules
        tests_dir = Path(__file__).parent / 'tests'
        test_modules = [f.stem for f in tests_dir.glob('test_*.py')]

        print("Available test modules:")
        for module in sorted(test_modules):
            print(f"  - {module}")
        return

    if args.module:
        # Run specific module
        result = run_specific_test_module(args.module, args.verbosity)
        if result is None:
            sys.exit(1)
    else:
        # Run all tests
        result = run_all_tests(args.verbosity, args.report)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()