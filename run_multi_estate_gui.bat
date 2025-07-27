@echo off
echo Analisis Verifikasi Transaksi Multi Estate FFB Scanner
echo ======================================================
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
echo Memulai GUI Analisis Verifikasi Multi Estate...
echo.

REM Run the Multi Estate GUI
python gui_multi_estate_analysis.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Terjadi error. Tekan tombol apa saja untuk keluar.
    pause >nul
) 