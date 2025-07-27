@echo off
echo Test Multi-Estate FFB GUI
echo =========================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python tidak terinstall atau tidak ada di PATH
    echo Silakan install Python 3.7 atau lebih tinggi
    pause
    exit /b 1
)

echo Python ditemukan
echo Menjalankan test system...
echo.

REM Run the test
python test_multi_estate_gui.py

echo.
echo Test selesai
pause 