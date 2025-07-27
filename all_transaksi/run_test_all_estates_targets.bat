@echo off
echo ========================================
echo TEST TARGET DIFFERENCES SEMUA ESTATE
echo ========================================
echo.

cd /d "%~dp0"

echo Menjalankan test target differences semua Estate...
python test_all_estates_targets.py

echo.
echo Test selesai. Tekan tombol apa saja untuk keluar...
pause > nul 