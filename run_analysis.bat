@echo off
echo ===================================================
echo  Analisis Perbedaan Data Panen Kerani dan Asisten
echo ===================================================
echo.
echo Menjalankan analisis...
echo.
python analisis_perbedaan_panen.py --use-localhost --limit 100
echo.
echo ===================================================
echo Analisis selesai! Laporan tersimpan di folder 'reports'.
echo.
echo Tekan tombol apa saja untuk keluar...
pause > nul
