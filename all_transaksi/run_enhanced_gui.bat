@echo off
title Enhanced GUI Ifess Analysis Tool v3.0
color 0A

echo ============================================================
echo ENHANCED GUI IFESS ANALYSIS TOOL v3.0
echo ============================================================
echo.
echo Enhanced Features:
echo [+] Comprehensive employee performance analysis
echo [+] Dual verification logic (Status 704 + Multiple records)
echo [+] RECORDTAG-based role determination
echo [+] 4-Sheet Excel reports (Detail, Role, Division, Status)
echo [+] Professional PDF reports with executive summary
echo [+] Advanced 2x3 visualization charts
echo [+] Enhanced Reports tab with real-time monitoring
echo.
echo Starting Enhanced GUI...
echo.

python run_enhanced_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo ERROR: Failed to start Enhanced GUI
    echo ============================================================
    echo.
    echo Possible solutions:
    echo 1. Install Python 3.7+ if not installed
    echo 2. Install required dependencies:
    echo    pip install pandas matplotlib seaborn reportlab openpyxl
    echo 3. Ensure firebird_connector.py is in the same directory
    echo 4. Check database file path and permissions
    echo.
    echo Press any key to exit...
    pause >nul
) else (
    echo.
    echo Enhanced GUI closed successfully.
)

echo.
echo Press any key to exit...
pause >nul 