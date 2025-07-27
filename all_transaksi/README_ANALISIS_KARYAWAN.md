# ANALISIS KINERJA KARYAWAN FFB SCANNER

Sistem analisis untuk mengukur kinerja individu karyawan dalam transaksi FFB Scanner, termasuk tingkat verifikasi dan breakdown status transaksi per karyawan.

## FITUR UTAMA

### 1. Analisis Per Karyawan
- **Total Transaksi Dibuat**: Jumlah total transaksi yang dibuat oleh setiap karyawan
- **Tingkat Verifikasi**: Persentase transaksi yang sudah diverifikasi dari total yang dibuat
- **Breakdown Status**: Detail status transaksi (Verified, Pending, Rejected, dll.)
- **Transaksi Unik**: Menghitung transaksi unik yang dibuat dan diverifikasi

### 2. Analisis Per Role
- **Kerani**: Fokus pada total transaksi dibuat dan tingkat verifikasi
- **Asisten/Mandor**: Statistik verifikasi dan kontribusi dalam proses validasi
- **Admin**: Aktivitas administrative dan verifikasi
- **Lainnya**: Karyawan dengan role tidak terdefinisi

### 3. Visualisasi Data
- Chart tingkat verifikasi per karyawan (Top 15)
- Chart total transaksi dibuat per karyawan (Top 15)  
- Summary jumlah karyawan per role
- Rata-rata tingkat verifikasi per role

### 4. Laporan Lengkap
- **Excel Report**: 3 sheets (Detail Karyawan, Summary Role, Breakdown Status)
- **PDF Report**: Laporan eksekutif dengan tabel dan visualisasi
- **Charts**: Grafik kinerja dalam format PNG

## CARA PENGGUNAAN

### Metode 1: Menggunakan Batch File (Mudah)
```batch
# Double-click file ini:
run_analisis_karyawan.bat
```

Pilihan yang tersedia:
1. **Analisis bulan ini** (default)
2. **Analisis bulan tertentu** (input: YYYY-MM)
3. **Analisis periode custom** (input: start-date dan end-date)
4. **Analisis dengan data terbatas** (untuk testing)

### Metode 2: Command Line
```bash
# Analisis bulan ini
python analisis_per_karyawan.py

# Analisis bulan tertentu
python analisis_per_karyawan.py --month 2025-06

# Analisis periode custom
python analisis_per_karyawan.py --start-date 2025-06-01 --end-date 2025-06-30

# Dengan data terbatas (testing)
python analisis_per_karyawan.py --limit 1000

# Custom database path
python analisis_per_karyawan.py --db-path "D:\Custom\Path\MILL04.FDB"

# Custom output directory
python analisis_per_karyawan.py --output-dir "D:\Custom\Reports"
```

## STRUKTUR OUTPUT

### 1. File Excel (analisis_karyawan_YYYYMMDD_HHMMSS_laporan_karyawan.xlsx)
**Sheet 1: Detail Karyawan**
- Nama Karyawan
- Role (KERANI/ASISTEN/MANDOR/ADMIN/LAINNYA)
- Total Transaksi Dibuat
- Transaksi Unik Dibuat
- Total Verifikasi Dilakukan
- Transaksi Unik Diverifikasi
- Tingkat Verifikasi (%)

**Sheet 2: Summary Role**
- Role
- Jumlah Karyawan
- Total Transaksi Dibuat
- Total Verifikasi Dilakukan
- Rata-rata Tingkat Verifikasi (%)

**Sheet 3: Breakdown Status**
- Nama Karyawan
- Role
- Status Transaksi
- Jumlah per Status

### 2. File PDF (analisis_karyawan_YYYYMMDD_HHMMSS_laporan_karyawan.pdf)
- Ringkasan Eksekutif
- Top 10 Karyawan dengan Tingkat Verifikasi Tertinggi
- Visualisasi Data (Charts)

### 3. File Chart (analisis_karyawan_YYYYMMDD_HHMMSS_kinerja_karyawan.png)
- 4 grafik dalam 1 file:
  - Top 15 Karyawan - Tingkat Verifikasi
  - Top 15 Karyawan - Total Transaksi Dibuat
  - Jumlah Karyawan per Role
  - Rata-rata Tingkat Verifikasi per Role

## INTERPRETASI HASIL

### Tingkat Verifikasi
- **Hijau (≥80%)**: Kinerja Sangat Baik
- **Orange (60-79%)**: Kinerja Baik
- **Merah (<60%)**: Perlu Perbaikan

### Key Performance Indicators (KPI)

**Untuk Kerani:**
- Target tingkat verifikasi: ≥90%
- Konsistensi dalam pembuatan transaksi
- Minimalisasi transaksi dengan status error

**Untuk Asisten/Mandor:**
- Efektivitas proses verifikasi
- Kecepatan response dalam validasi
- Akurasi dalam proses approval

**Untuk Manajemen:**
- Overall verification rate per departemen
- Identifikasi bottleneck dalam proses
- Training needs analysis

## TROUBLESHOOTING

### Error Database Connection
```
Error: Gagal terhubung ke database!
```
**Solusi:**
1. Periksa path database di script atau parameter --db-path
2. Pastikan database Firebird berjalan
3. Verifikasi credential (username/password)

### Error Missing Dependencies
```
ModuleNotFoundError: No module named 'pandas'
```
**Solusi:**
```bash
pip install pandas matplotlib seaborn openpyxl reportlab
```

### Error Firebird ISQL
```
FileNotFoundError: isql.exe tidak ditemukan
```
**Solusi:**
1. Install Firebird client
2. Tambahkan path Firebird ke system PATH

### Tidak Ada Data
```
Tidak ada data transaksi yang ditemukan!
```
**Solusi:**
1. Periksa periode analisis (pastikan ada data di tanggal tersebut)
2. Periksa nama tabel (FFBSCANNERDATA + nomor bulan)
3. Verifikasi koneksi database

## KONFIGURASI

### Default Settings
- **Database Path**: `D:\IFESS Firebird Database\MILL04.FDB`
- **Output Directory**: `./reports/`
- **Periode Default**: Bulan berjalan
- **Username**: `sysdba`
- **Password**: `masterkey`

### Custom Configuration
Edit bagian ini di script untuk konfigurasi permanen:
```python
# Koneksi database
db_path = args.db_path or r'D:\IFESS Firebird Database\MILL04.FDB'

# Default mapping karyawan
default_mapping = {
    '4771': 'KERANI_DEFAULT',
    '5044': 'ASISTEN_DEFAULT',
    # Tambahkan mapping lainnya...
}
```

## MAINTENANCE

### Update Mapping Karyawan
Jika ada karyawan baru atau perubahan nama, update di fungsi `get_employee_mapping()`:
```python
default_mapping = {
    'ID_BARU': 'NAMA_KARYAWAN',
    # ...
}
```

### Update Status Mapping  
Untuk status transaksi baru, update di fungsi `get_transstatus_mapping()`:
```python
default_mapping = {
    'STATUS_ID': 'DESKRIPSI_STATUS',
    # ...
}
```

## SUPPORT

Untuk pertanyaan atau bantuan, hubungi tim IT atau developer sistem.

**Log Files**: Periksa console output untuk debugging information.

**Performance**: Untuk database besar, gunakan parameter `--limit` untuk testing awal.

---
*Generated by Analisis Kinerja Karyawan FFB Scanner v1.0*