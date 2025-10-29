#!/usr/bin/env python3
"""
Fix Relative Imports Script
Converts all relative imports to absolute imports in the project
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix relative imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Pattern to match relative imports
        # from ..module import Class
        # from ...package.module import Class
        pattern = r'from \.+([\w.]+) import ([\w, ]+)'

        def replace_import(match):
            relative_path = match.group(1)
            imports = match.group(2)

            # Count the number of dots to determine the level
            dots_count = len(re.match(r'^\.+', match.group(0)).group())

            # Convert relative path to absolute path
            if relative_path.startswith('.'):
                absolute_path = relative_path.lstrip('.')
            else:
                absolute_path = relative_path

            return f'from {absolute_path} import {imports}'

        # Apply the replacement
        content = re.sub(pattern, replace_imports, content)

        # Special handling for ..module cases
        pattern2 = r'from \.\.([\w]+) import ([\w, ]+)'
        content = re.sub(pattern2, r'from \1 import \2', content)

        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

    return False

def fix_all_imports():
    """Fix all relative imports in the src directory"""
    src_dir = Path("src")

    if not src_dir.exists():
        print("src directory not found!")
        return

    python_files = list(src_dir.rglob("*.py"))
    fixed_count = 0

    print(f"Found {len(python_files)} Python files...")

    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1

    print(f"\nFixed imports in {fixed_count} files.")

if __name__ == "__main__":
    fix_all_imports()