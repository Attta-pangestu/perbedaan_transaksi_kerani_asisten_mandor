#!/usr/bin/env python3
"""
Test script untuk menjalankan Enhanced GUI Ifess Analysis Tool
dengan fitur comprehensive reporting yang telah diintegrasikan.

Features yang telah ditambahkan:
1. Enhanced analysis dengan dual verification logic
2. RECORDTAG-based role determination
3. 4-sheet Excel reports
4. Comprehensive PDF reports
5. Advanced visualization charts
6. Enhanced Reports tab dengan status monitoring
"""

import sys
import os
import traceback

def main():
    """Main function untuk menjalankan Enhanced GUI."""
    try:
        print("=" * 60)
        print("IFESS DATABASE ANALYSIS TOOL v3.0 - ENHANCED")
        print("=" * 60)
        print()
        print("Enhanced Features:")
        print("✓ Comprehensive employee performance analysis")
        print("✓ Dual verification logic (Status 704 + Multiple records)")
        print("✓ RECORDTAG-based role determination (PM=KERANI, P1=ASISTEN, P5=MANDOR)")
        print("✓ 4-Sheet Excel reports (Detail, Role Summary, Division Summary, Status Breakdown)")
        print("✓ Professional PDF reports with executive summary")
        print("✓ Advanced 2x3 visualization charts")
        print("✓ Enhanced Reports tab with real-time status")
        print()
        print("Starting Enhanced GUI...")
        print()
        
        # Import dan jalankan GUI
        from gui_ifess_analysis import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print()
        print("Required modules:")
        print("- tkinter (GUI framework)")
        print("- pandas (data processing)")
        print("- firebird_connector (database connection)")
        print("- matplotlib/seaborn (for charts)")
        print("- reportlab (for PDF generation)")
        print("- openpyxl (for Excel export)")
        print()
        print("Please install missing dependencies:")
        print("pip install pandas matplotlib seaborn reportlab openpyxl")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 