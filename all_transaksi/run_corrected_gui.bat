@echo off
echo FFB Scanner Analysis GUI - Corrected Logic
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python tidak ditemukan
    echo Silakan install Python terlebih dahulu
    pause
    exit /b 1
)

echo Python ditemukan
echo Memeriksa dependencies...

REM Check required modules
python -c "import tkinter, pandas, tkcalendar, reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Beberapa module Python tidak ditemukan
    echo Silakan install dependencies dengan perintah:
    echo pip install pandas tkcalendar reportlab
    pause
    exit /b 1
)

echo Dependencies tersedia
echo Memulai GUI dengan logika yang benar...

REM Run the corrected GUI
python gui_ffb_analysis_corrected.py

echo.
echo GUI selesai
pause 