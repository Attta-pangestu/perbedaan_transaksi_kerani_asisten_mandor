@echo off
echo ===============================================
echo SISTEM ANALISIS FFB MULTI-ESTATE (ENHANCED)
echo dengan Filter TRANSSTATUS 704
echo ===============================================
echo.

cd /d "%~dp0"

echo Menjalankan sistem analisis FFB yang telah diperbaiki...
echo.
echo Fitur yang tersedia:
echo - Filter TRANSSTATUS 704 untuk Estate 1A bulan Mei 2025
echo - Perhitungan perbedaan input antara Kerani dan Mandor/Asisten
echo - Prioritas P1 (Asisten) atas P5 (Mandor)
echo - Display persentase terverifikasi dengan jumlah dalam tanda kurung
echo - Kolom keterangan dengan jumlah perbedaan input
echo.

python gui_multi_estate_ffb_analysis.py

echo.
echo Sistem selesai dijalankan.
echo Tekan tombol apa saja untuk menutup...
pause > nul 