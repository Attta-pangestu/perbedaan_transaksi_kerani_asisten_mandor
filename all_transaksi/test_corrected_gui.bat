@echo off
echo FFB Scanner Analysis GUI - Logic Verification Test
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python tidak ditemukan
    echo Silakan install Python terlebih dahulu
    pause
    exit /b 1
)

echo Python ditemukan
echo Menjalankan test untuk memverifikasi logika GUI...

REM Run the test
python test_corrected_gui.py

echo.
echo Test selesai
pause 