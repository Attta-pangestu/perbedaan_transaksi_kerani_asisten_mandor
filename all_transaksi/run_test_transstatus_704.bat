@echo off
echo ===============================================
echo TEST FILTER TRANSSTATUS 704 - ESTATE 1A MEI 2025
echo ===============================================
echo.

cd /d "%~dp0"

echo Menjalankan test filter TRANSSTATUS 704...
python test_transstatus_704_filter.py

echo.
echo Test selesai. Tekan tombol apa saja untuk menutup...
pause > nul 