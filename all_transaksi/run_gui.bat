@echo off
echo FFB Scanner Analysis GUI
echo ========================
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
echo Memulai GUI...
echo.

REM Run the GUI
python run_simple_gui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Terjadi error. Tekan tombol apa saja untuk keluar.
    pause >nul
)
