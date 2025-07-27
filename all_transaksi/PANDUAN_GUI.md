# Panduan Penggunaan GUI FFB Scanner Analysis

## Cara Menjalankan

### Metode 1: Double-click file batch (Recommended)
1. Double-click file `run_gui.bat`
2. GUI akan terbuka otomatis

### Metode 2: Melalui Python
1. Buka command prompt di folder ini
2. Jalankan: `python run_simple_gui.py`

## Fitur GUI

### 1. Pilih Rentang Tanggal
- **Tanggal Mulai**: Tanggal awal analisis
- **Tanggal Akhir**: Tanggal akhir analisis
- **Tombol Cepat**:
  - **April 2025 (Test)**: Set ke 1-28 April 2025 untuk testing
  - **Bulan Ini**: Set ke bulan berjalan
  - **Bulan Lalu**: Set ke bulan sebelumnya

### 2. Pilih Divisi
- **Semua Divisi**: Analisis semua divisi yang tersedia
- **Divisi Tertentu**: Pilih divisi spesifik dari daftar
  - Gunakan Ctrl+Click untuk pilih multiple
  - Divisi utama (Air Batu, Air Kundo, Air Hijau) sudah dipilih secara default

### 3. Menjalankan Analisis
1. Pilih rentang tanggal
2. Pilih divisi yang ingin dianalisis
3. Click "Mulai Analisis"
4. Tunggu proses selesai
5. Laporan Excel akan dibuat otomatis

## Hasil Analisis

### Laporan Excel
- Disimpan di folder `reports/`
- Format nama: `laporan_mandor_per_divisi_MM_YYYY_timestamp.xlsx`
- Berisi:
  - Summary semua divisi
  - Detail per divisi
  - Breakdown per karyawan
  - Verification rates

### Contoh Output untuk Air Kundo
Setelah perbaikan script, hasil untuk Erly (SCANUSERID 4771) seharusnya menunjukkan:
- **123 transaksi** (sesuai query yang Anda berikan)
- Role: KERANI (PM transactions)
- Periode: 1-28 April 2025

## Perbaikan yang Dilakukan

### 1. Date Range Correction
- Menggunakan `< '2025-04-29'` sesuai query user
- Menghilangkan duplikasi perhitungan transaksi

### 2. Transaction Counting Fix
- Menghitung transaksi hanya sekali (tidak duplikasi)
- Memisahkan perhitungan total transaksi dan verifikasi
- Menggunakan `verification_stats` untuk tracking yang akurat

### 3. Role Mapping
- PM = KERANI (Bunch Counter)
- P1 = MANDOR (Conductor) 
- P5 = ASISTEN (Assistant)

## Troubleshooting

### GUI Tidak Muncul
- Pastikan Python terinstall
- Jalankan dari command prompt untuk melihat error

### Database Connection Failed
- Pastikan path database benar: `C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB`
- Pastikan Firebird terinstall

### Hasil Tidak Sesuai
- Periksa rentang tanggal
- Pastikan divisi yang dipilih benar
- Cek apakah data ada di periode tersebut

### Dependencies Missing
Jika ada error tentang missing packages:
```bash
pip install pandas tkcalendar openpyxl
```

## Verifikasi Hasil

Untuk memverifikasi hasil Erly di Air Kundo:
```sql
SELECT COUNT(*) 
FROM FFBSCANNERDATA04 a 
JOIN OCFIELD b ON a.FIELDID = b.ID 
WHERE b.DIVID = '16' 
    AND a.RECORDTAG = 'PM' 
    AND a.SCANUSERID = '4771' 
    AND a.TRANSDATE >= '2025-04-01' 
    AND a.TRANSDATE < '2025-04-29'
```

Hasil seharusnya: **123 transaksi**

## Catatan Penting

1. **Date Format**: Gunakan format YYYY-MM-DD jika input manual
2. **Month Selection**: GUI otomatis memilih tabel yang sesuai berdasarkan bulan
3. **Performance**: Analisis besar mungkin membutuhkan waktu lebih lama
4. **Reports**: File laporan disimpan dengan timestamp untuk menghindari overwrite

GUI ini menyediakan interface yang mudah untuk melakukan analisis FFB scanner dengan rentang tanggal yang fleksibel, sesuai permintaan Anda.
