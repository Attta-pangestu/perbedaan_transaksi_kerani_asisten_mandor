#!/usr/bin/env python3
"""
Simple test sistem untuk memastikan semua komponen bekerja
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

def test_all_imports():
    """Test semua imports"""
    print("Testing all imports...")

    try:
        # Test database connector
        from firebird_connector import FirebirdConnector
        print("  [OK] firebird_connector imported")

        # Test template manager
        from template_manager import TemplateManager
        print("  [OK] template_manager imported")

        # Test analysis engine
        from ffb_analysis_engine import FFBAnalysisEngine
        print("  [OK] ffb_analysis_engine imported")

        # Test report generator
        from report_generator import ReportGenerator
        print("  [OK] report_generator imported")

        # Test GUI components
        import tkinter as tk
        from main_gui import FFBReportingSystemGUI
        print("  [OK] GUI components imported")

        return True

    except Exception as e:
        print(f"  [ERROR] Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("Testing basic functionality...")

    try:
        from template_manager import TemplateManager
        from ffb_analysis_engine import FFBAnalysisEngine
        from report_generator import ReportGenerator

        # Test template manager
        manager = TemplateManager("../templates")
        templates = manager.get_all_templates()
        print(f"  [OK] TemplateManager: {len(templates)} templates loaded")

        # Test analysis engine
        engine = FFBAnalysisEngine()
        print("  [OK] FFBAnalysisEngine initialized")

        # Test report generator
        generator = ReportGenerator("../reports")
        print("  [OK] ReportGenerator initialized")

        return True

    except Exception as e:
        print(f"  [ERROR] Functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("SIMPLE SYSTEM TEST")
    print("=" * 50)

    # Setup paths
    setup_paths()

    # Run tests
    print("\n1. Import Test:")
    import_success = test_all_imports()

    if import_success:
        print("\n2. Functionality Test:")
        func_success = test_basic_functionality()
    else:
        func_success = False

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    if import_success and func_success:
        print("[SUCCESS] All tests passed!")
        print("System is ready to use.")
        print("\nTo start the application, run:")
        print("python start_app.py")
        return True
    else:
        print("[FAILED] Some tests failed.")
        print("Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)