#!/usr/bin/env python3
"""
Test script untuk memastikan semua import berjalan dengan benar
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test semua module imports"""
    print("Testing imports...")

    # Test firebird_connector
    try:
        # Add parent directory to path
        parent_path = Path(__file__).parent
        sys.path.insert(0, str(parent_path))

        from firebird_connector import FirebirdConnector
        print("✓ firebird_connector imported successfully")
    except Exception as e:
        print(f"✗ firebird_connector import failed: {e}")
        return False

    # Test GUI imports
    try:
        # Change to src directory
        src_path = Path(__file__).parent / "src"
        os.chdir(src_path)
        sys.path.insert(0, str(src_path))

        from template_manager import TemplateManager
        print("✓ template_manager imported successfully")
    except Exception as e:
        print(f"✗ template_manager import failed: {e}")
        return False

    try:
        from report_generator import ReportGenerator
        print("✓ report_generator imported successfully")
    except Exception as e:
        print(f"✗ report_generator import failed: {e}")
        return False

    try:
        from ffb_analysis_engine import FFBAnalysisEngine
        print("✓ ffb_analysis_engine imported successfully")
    except Exception as e:
        print(f"✗ ffb_analysis_engine import failed: {e}")
        return False

    try:
        from main_gui import FFBReportingSystemGUI
        print("✓ main_gui imported successfully")
    except Exception as e:
        print(f"✗ main_gui import failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 50)
    print("IMPORT TEST FOR FFB REPORTING SYSTEM")
    print("=" * 50)

    success = test_imports()

    if success:
        print("\n✅ All imports successful!")
        print("Application should start without import errors.")
    else:
        print("\n❌ Some imports failed!")
        print("Please check the error messages above.")

    input("\nPress Enter to exit...")