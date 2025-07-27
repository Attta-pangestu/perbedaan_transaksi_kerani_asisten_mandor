@echo off
echo FFB Scanner Multi-Estate Analysis GUI - PDF Report
echo ================================================
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
echo Memeriksa dependencies...

REM Check required modules
python -c "import tkinter, pandas, tkcalendar, fdb, reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Beberapa module Python tidak ditemukan
    echo Silakan install dependencies dengan perintah:
    echo pip install pandas tkcalendar fdb reportlab
    pause
    exit /b 1
)

echo Dependencies tersedia
echo Memulai Multi-Estate GUI dengan PDF Report...
echo.

REM Run the multi-estate GUI
python gui_multi_estate_ffb_analysis.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Terjadi error. Tekan tombol apa saja untuk keluar.
    pause >nul
) 