#!/usr/bin/env python3
"""
Launcher untuk GUI FFB Scanner Analysis
"""

import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check if required packages are available"""
    try:
        import tkinter
        print("✓ tkinter tersedia")
    except ImportError:
        print("✗ tkinter tidak tersedia")
        return False
    
    try:
        import pandas
        print("✓ pandas tersedia")
    except ImportError:
        print("✗ pandas tidak tersedia")
        print("Install dengan: pip install pandas")
        return False
    
    try:
        import tkcalendar
        print("✓ tkcalendar tersedia")
    except ImportError:
        print("⚠ tkcalendar tidak tersedia (opsional)")
        print("Install dengan: pip install tkcalendar")
        print("GUI akan menggunakan input teks untuk tanggal")
    
    return True

def main():
    """Main launcher"""
    print("FFB Scanner Analysis GUI Launcher")
    print("=" * 40)
    
    if not check_dependencies():
        print("\nError: Dependensi yang diperlukan tidak tersedia")
        input("Tekan Enter untuk keluar...")
        return
    
    print("\nMemulai GUI...")
    
    try:
        from ffb_gui_simple import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error: Tidak dapat mengimpor GUI module: {e}")
        input("Tekan Enter untuk keluar...")
    except Exception as e:
        print(f"Error: {e}")
        input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
