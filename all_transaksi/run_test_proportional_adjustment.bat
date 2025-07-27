@echo off
echo ========================================
echo TEST PENYESUAIAN PROPORSIONAL
echo ========================================
echo.

cd /d "%~dp0"

echo Menjalankan test penyesuaian proporsional...
python test_proportional_adjustment.py

echo.
echo Test selesai. Tekan tombol apa saja untuk keluar...
pause > nul 