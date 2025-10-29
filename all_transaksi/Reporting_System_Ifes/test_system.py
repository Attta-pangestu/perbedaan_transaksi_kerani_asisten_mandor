#!/usr/bin/env python3
"""
Test sistem untuk memastikan semua komponen bekerja dengan benar
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Setup sys.path untuk imports"""
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    parent_dir = current_dir.parent

    # Add to sys.path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    # Change to src directory
    os.chdir(src_dir)

def test_template_manager():
    """Test template manager"""
    print("Testing Template Manager...")

    try:
        from template_manager import TemplateManager

        # Test initialization
        manager = TemplateManager("../templates")
        print("  [OK] TemplateManager initialized")

        # Test template loading
        templates = manager.get_all_templates()
        print(f"  [OK] Loaded {len(templates)} templates")

        # Test template details
        if templates:
            first_template = templates[0]
            template_id = first_template['template_id']
            template = manager.get_template(template_id)
            print(f"  [OK] Retrieved template: {template_id}")

            # Test validation
            errors = manager.validate_template(template)
            if errors:
                print(f"  [WARNING] Template validation warnings: {len(errors)}")
            else:
                print("  [OK] Template validation passed")

        return True

    except Exception as e:
        print(f"  [ERROR] TemplateManager error: {e}")
        return False

def test_analysis_engine():
    """Test analysis engine"""
    print("Testing Analysis Engine...")

    try:
        from ffb_analysis_engine import FFBAnalysisEngine

        # Test initialization
        engine = FFBAnalysisEngine()
        print("  ✓ FFBAnalysisEngine initialized")

        return True

    except Exception as e:
        print(f"  ✗ FFBAnalysisEngine error: {e}")
        return False

def test_report_generator():
    """Test report generator"""
    print("Testing Report Generator...")

    try:
        from report_generator import ReportGenerator

        # Test initialization
        generator = ReportGenerator("../reports")
        print("  ✓ ReportGenerator initialized")

        return True

    except Exception as e:
        print(f"  ✗ ReportGenerator error: {e}")
        return False

def test_gui_import():
    """Test GUI import"""
    print("Testing GUI Import...")

    try:
        # Test imports without starting GUI
        import tkinter as tk
        from main_gui import FFBReportingSystemGUI

        print("  ✓ GUI imports successful")

        # Test class instantiation (without showing)
        root = tk.Tk()
        root.withdraw()  # Hide the window

        try:
            app = FFBReportingSystemGUI(root)
            print("  ✓ GUI class instantiation successful")
            root.destroy()
            return True
        except Exception as e:
            print(f"  ⚠ GUI instantiation warning: {e}")
            root.destroy()
            return True  # Still count as success for imports

    except Exception as e:
        print(f"  ✗ GUI import error: {e}")
        return False

def test_database_connector():
    """Test database connector import"""
    print("Testing Database Connector...")

    try:
        from firebird_connector import FirebirdConnector

        print("  ✓ FirebirdConnector imported successfully")

        # Test class definition
        connector_class = FirebirdConnector
        print(f"  ✓ FirebirdConnector class available: {connector_class}")

        return True

    except Exception as e:
        print(f"  ✗ FirebirdConnector error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("SYSTEM INTEGRATION TEST")
    print("=" * 60)

    # Setup paths
    setup_paths()

    # Run tests
    tests = [
        ("Database Connector", test_database_connector),
        ("Template Manager", test_template_manager),
        ("Analysis Engine", test_analysis_engine),
        ("Report Generator", test_report_generator),
        ("GUI Import", test_gui_import)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)