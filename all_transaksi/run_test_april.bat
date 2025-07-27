@echo off
title Test Data April 2025
color 0A

echo ========================================
echo     TEST DATA APRIL 2025
echo ========================================
echo.

cd /d "%~dp0"

echo Running April data test...
python test_april_data.py

echo.
echo ========================================
echo     Running Main Analysis (April)
echo ========================================
echo.

python analisis_mandor_per_divisi_corrected.py

echo.
echo ========================================
echo     Verifying Results Against Expected Data
echo ========================================
echo.

python verify_april_results.py

echo.
echo Test completed! Check the reports folder for results.
pause 