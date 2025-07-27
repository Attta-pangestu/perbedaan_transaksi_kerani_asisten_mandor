#!/usr/bin/env python3
"""
Install PDF dependencies for FFB Scanner Report
"""

import subprocess
import sys

def install_dependencies():
    """Install required packages for PDF generation"""
    packages = [
        'reportlab',
        'pandas',
        'openpyxl'
    ]
    
    print("Installing PDF Report Dependencies...")
    print("="*50)
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e}")
            return False
    
    print("\n✅ All dependencies installed successfully!")
    print("You can now run the GUI with PDF report generation.")
    return True

if __name__ == "__main__":
    install_dependencies()
