@echo off
echo ========================================
echo LAPORAN KINERJA KERANI, MANDOR, ASISTEN
echo ========================================
echo.

cd /d "%~dp0"

echo Menjalankan GUI Laporan Kinerja...
python gui_multi_estate_ffb_analysis.py

echo.
echo GUI selesai. Tekan tombol apa saja untuk keluar...
pause > nul 