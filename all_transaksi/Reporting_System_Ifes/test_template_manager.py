#!/usr/bin/env python3
"""
Test spesifik untuk template manager
"""

import os
import sys
from pathlib import Path

def setup_paths():
    """Setup paths seperti di start_app.py"""
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    sys.path.insert(0, str(src_dir))
    os.chdir(src_dir)

def test_template_manager():
    """Test template manager"""
    print("TESTING TEMPLATE MANAGER")
    print("=" * 40)

    try:
        from template_manager import TemplateManager

        # Cek current working directory
        print(f"Current working directory: {os.getcwd()}")

        # Test path resolution
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(current_file)
        templates_dir = os.path.join(src_dir, "..", "templates")
        templates_dir = os.path.abspath(templates_dir)

        print(f"Expected templates directory: {templates_dir}")
        print(f"Templates directory exists: {os.path.exists(templates_dir)}")

        if os.path.exists(templates_dir):
            files = os.listdir(templates_dir)
            print(f"Files in templates: {files}")
        else:
            print("Templates directory NOT found!")

        # Initialize TemplateManager
        print("\nInitializing TemplateManager...")
        manager = TemplateManager()
        print(f"TemplateManager.templates_dir: {manager.templates_dir}")
        print(f"Templates found: {len(manager.templates)}")

        if manager.templates:
            for template_id, template in manager.templates.items():
                print(f"  - {template_id}: {template.get('name', 'Unknown')}")
        else:
            print("No templates loaded!")

        # Test specific file check
        template_file = os.path.join(manager.templates_dir, "laporan_verifikasi_multi_estate.json")
        print(f"\nTemplate file path: {template_file}")
        print(f"Template file exists: {os.path.exists(template_file)}")

        if os.path.exists(template_file):
            try:
                import json
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Template loaded successfully: {data.get('template_id', 'Unknown ID')}")
            except Exception as e:
                print(f"Error loading template file: {e}")

        return len(manager.templates) > 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_paths()
    success = test_template_manager()
    if success:
        print("\n[SUCCESS] Template Manager working!")
    else:
        print("\n[FAILED] Template Manager issues detected!")