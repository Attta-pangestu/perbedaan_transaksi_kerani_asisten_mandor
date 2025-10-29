#!/usr/bin/env python3
"""
Simple test untuk path checking
"""

import sys
import os
from pathlib import Path

def check_paths():
    """Check if all required files exist"""
    print("Checking file paths...")

    # Current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")

    # Check firebird_connector.py
    firebird_path = Path("../firebird_connector.py")
    print(f"Looking for firebird_connector at: {firebird_path.absolute()}")
    if firebird_path.exists():
        print("OK: firebird_connector.py found")
    else:
        print("ERROR: firebird_connector.py not found")

        # Try other paths
        alt_paths = [
            Path("../../firebird_connector.py"),
            Path("firebird_connector.py"),
            Path("../firebird_connector.py")
        ]

        for alt_path in alt_paths:
            if alt_path.exists():
                print(f"Found at: {alt_path.absolute()}")
                break

    # Check config.json
    config_path = Path("../config.json")
    print(f"Looking for config.json at: {config_path.absolute()}")
    if config_path.exists():
        print("OK: config.json found")
    else:
        print("ERROR: config.json not found")

    # Check templates directory
    templates_path = Path("../templates")
    print(f"Looking for templates at: {templates_path.absolute()}")
    if templates_path.exists():
        print("OK: templates directory found")
        template_files = list(templates_path.glob("*.json"))
        print(f"Found {len(template_files)} template files")
    else:
        print("ERROR: templates directory not found")

    # List sys.path
    print("\nCurrent sys.path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

def test_simple_import():
    """Test simple import"""
    print("\nTesting simple import...")

    try:
        # Add parent directory to sys.path
        parent_dir = Path("../").absolute()
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))

        print(f"Added to sys.path: {parent_dir}")

        # Try import
        import firebird_connector
        print("SUCCESS: firebird_connector imported")

        # Test class instantiation
        connector_class = firebird_connector.FirebirdConnector
        print(f"SUCCESS: FirebirdConnector class found: {connector_class}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SIMPLE PATH AND IMPORT TEST")
    print("=" * 60)

    check_paths()

    success = test_simple_import()

    if success:
        print("\n*** SUCCESS: All tests passed! ***")
    else:
        print("\n*** FAILED: Import issues detected ***")

    input("\nPress Enter to exit...")