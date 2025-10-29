#!/usr/bin/env python3
"""
Debug path resolution untuk template manager
"""

import os
import sys
from pathlib import Path

def debug_paths():
    """Debug path resolution"""
    print("DEBUG PATH RESOLUTION")
    print("=" * 50)

    # Current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    # Script location
    script_file = os.path.abspath(__file__)
    print(f"Script location: {script_file}")

    # Simulate template_manager.py path resolution
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file)
    parent_dir = os.path.dirname(src_dir)
    templates_dir = os.path.join(parent_dir, "templates")

    print(f"Simulated src_dir: {src_dir}")
    print(f"Simulated parent_dir: {parent_dir}")
    print(f"Simulated templates_dir: {templates_dir}")
    print(f"Templates dir exists: {os.path.exists(templates_dir)}")

    # List files in templates directory
    if os.path.exists(templates_dir):
        files = os.listdir(templates_dir)
        print(f"Files in templates dir: {files}")
    else:
        print("Templates directory does not exist!")

    # Check actual template file
    template_file = os.path.join(templates_dir, "laporan_verifikasi_multi_estate.json")
    print(f"Template file path: {template_file}")
    print(f"Template file exists: {os.path.exists(template_file)}")

    # Add src to sys.path (simulating start_app.py)
    sys.path.insert(0, src_dir)
    print(f"Added to sys.path: {src_dir}")

    # Try import
    try:
        from template_manager import TemplateManager
        print("TemplateManager import successful")

        # Test initialization
        manager = TemplateManager()
        print(f"TemplateManager.templates_dir: {manager.templates_dir}")
        print(f"Template manager templates count: {len(manager.templates)}")

    except Exception as e:
        print(f"TemplateManager import/initialization error: {e}")

def test_alternative_paths():
    """Test alternative path resolutions"""
    print("\nALTERNATIVE PATH RESOLUTION")
    print("=" * 50)

    # Method 1: Using Path from pathlib
    script_path = Path(__file__).resolve()
    src_path = script_path.parent
    parent_path = src_path.parent
    templates_path = parent_path / "templates"

    print(f"Pathlib - script_path: {script_path}")
    print(f"Pathlib - src_path: {src_path}")
    print(f"Pathlib - parent_path: {parent_path}")
    print(f"Pathlib - templates_path: {templates_path}")
    print(f"Pathlib - templates exists: {templates_path.exists()}")

    # Method 2: Relative from current working directory
    current_dir = Path.cwd()
    templates_relative = current_dir / "templates"

    print(f"CWD - current_dir: {current_dir}")
    print(f"CWD - templates_relative: {templates_relative}")
    print(f"CWD - templates exists: {templates_relative.exists()}")

if __name__ == "__main__":
    debug_paths()
    test_alternative_paths()