# Analisis Detail Transaksi KERANI - FFB IFESS

## Deskripsi

Script `analisis_detail_kerani.py` adalah sistem analisis komprehensif yang dirancang khusus untuk menganalisis transaksi yang dilakukan oleh **KERANI** dalam sistem FFB (Fresh Fruit Bunch) IFESS. Script ini memberikan laporan detail yang mencakup:

1. **Detail Transaksi per TRANSNO dan TRANSDATE**
2. **Pengelompokan berdasarkan Divisi**
3. **Pasangan Kerja KERANI dengan MANDOR/ASISTEN**
4. **Analisis Verifikasi Transaksi**

## Fitur Utama

### 🔍 Analisis Komprehensif
- **Fokus pada KERANI**: Menganalisis khusus transaksi yang dibuat oleh karyawan dengan role KERANI
- **Detail TRANSNO**: Menampilkan semua TRANSNO yang dilakukan oleh setiap KERANI dalam periode tertentu
- **Pengelompokan Divisi**: Mengelompokkan KERANI berdasarkan divisi kerja
- **Pasangan Kerja**: Menampilkan pasangan KERANI dengan MANDOR/ASISTEN dalam setiap divisi

### 📊 Laporan Excel 4 Sheet
1. **Detail Transaksi KERANI**: Daftar lengkap semua transaksi KERANI
2. **Summary KERANI**: Ringkasan kinerja per KERANI
3. **Pengelompokan Divisi**: Analisis per divisi dengan pasangan kerja
4. **TRANSNO per Bulan**: Detail TRANSNO yang dikerjakan dalam satu bulan

### 🎯 Metrik Analisis
- **Total Transaksi**: Jumlah transaksi yang dibuat oleh KERANI
- **Transaksi Verified**: Jumlah transaksi yang telah diverifikasi oleh MANDOR/ASISTEN
- **Tingkat Verifikasi**: Persentase verifikasi dari total transaksi
- **Unique TRANSNO**: Jumlah TRANSNO unik yang dikerjakan
- **Daftar TRANSNO**: List lengkap TRANSNO per KERANI

## Struktur Laporan

### Sheet 1: Detail Transaksi KERANI
```
Nama KERANI | Divisi | TRANSNO | TRANSDATE | Status Code | Verified | RECORDTAG | Creator ID
```

### Sheet 2: Summary KERANI
```
Nama KERANI | Divisi Utama | Total Transaksi | Transaksi Verified | Tingkat Verifikasi (%) | Unique TRANSNO | TRANSNO List
```

### Sheet 3: Pengelompokan Divisi
```
Divisi | Jumlah KERANI | KERANI | Jumlah MANDOR/ASISTEN | MANDOR/ASISTEN | Total Transaksi KERANI | Transaksi Verified | Tingkat Verifikasi (%)
```

### Sheet 4: TRANSNO per Bulan
```
KERANI | Divisi | TRANSNO | Jumlah Entry | Tanggal Pertama | Tanggal Terakhir | Entry Verified | Status Verifikasi
```

## Penggunaan

### 1. Konfigurasi Database
Edit konfigurasi dalam `main()` function:
```python
# Konfigurasi
DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
OUTPUT_DIR = "reports"

# Periode analisis
MONTH = 5  # Mei
YEAR = 2025
```

### 2. Menjalankan Analisis

#### Method 1: Direct Python
```bash
python analisis_detail_kerani.py
```

#### Method 2: Batch File
```bash
run_analisis_detail_kerani.bat
```

### 3. Output Laporan
Laporan akan disimpan dalam folder `reports/` dengan format:
```
laporan_detail_kerani_05_2025_20250609_094200.xlsx
```

## Contoh Output Console

```
🚀 MEMULAI ANALISIS DETAIL TRANSAKSI KERANI
============================================================
📡 Menghubungkan ke database...
✓ Koneksi database berhasil
📋 Memuat mapping data...
Mengambil data dari FFBSCANNERDATA05...
Periode: 2025-05-01 sampai 2025-06-01
✓ Data berhasil diambil: 1500 record
🔍 Memulai analisis detail transaksi KERANI...
✓ Ditemukan 45 transaksi terverifikasi melalui deteksi duplikat
✓ Analisis selesai: 8 KERANI ditemukan
✓ Divisi yang terlibat: 3
📊 Membuat laporan detail KERANI...
✓ Laporan Excel disimpan: reports/laporan_detail_kerani_05_2025_20250609_094200.xlsx

================================================================================
RINGKASAN ANALISIS DETAIL KERANI
================================================================================
Periode Analisis: 05/2025
Total KERANI: 8
Total Transaksi KERANI: 342
Total Transaksi Verified: 298
Tingkat Verifikasi Keseluruhan: 87.13%
Total Divisi Terlibat: 3

DETAIL PER DIVISI:
📁 Air Batu:
   - KERANI: 3 orang (Ahmad Kerani, Siti Kerani, Budi Kerani)
   - MANDOR/ASISTEN: 2 orang (Joko Mandor, Andi Asisten)
   - Transaksi KERANI: 156
   - Verified: 142 (91.0%)

📁 Air Hijau:
   - KERANI: 3 orang (Dewi Kerani, Rini Kerani, Agus Kerani)
   - MANDOR/ASISTEN: 2 orang (Sari Mandor, Toni Asisten)
   - Transaksi KERANI: 124
   - Verified: 108 (87.1%)

📁 Sawit Indah:
   - KERANI: 2 orang (Maya Kerani, Indra Kerani)
   - MANDOR/ASISTEN: 1 orang (Hadi Mandor)
   - Transaksi KERANI: 62
   - Verified: 48 (77.4%)

DETAIL PER KERANI:
👤 Ahmad Kerani:
   - Total Transaksi: 67
   - Verified: 62 (92.5%)
   - Unique TRANSNO: 12
   - TRANSNO List: T001, T002, T003, T004, T005, T006, T007, T008, T009, T010, T011, T012

👤 Siti Kerani:
   - Total Transaksi: 54
   - Verified: 48 (88.9%)
   - Unique TRANSNO: 9
   - TRANSNO List: T013, T014, T015, T016, T017, T018, T019, T020, T021
```

## Informasi Teknis

### Dependencies
- pandas
- datetime
- os
- collections
- json
- firebird_connector (custom module)
- analisis_per_karyawan (custom module)

### Metode Verifikasi
1. **Status Code Verification**: Menggunakan status code 704 = VERIFIED
2. **Duplicate Detection**: Mendeteksi transaksi dengan TRANSNO dan TRANSDATE yang sama

### Role Detection
1. **Primary Method**: RECORDTAG mapping (PM=KERANI, P1=ASISTEN, P5=MANDOR)
2. **Fallback Method**: Name-based detection

### Column Mapping
```python
scanuserid_col = 1   # SCANUSERID
recordtag_col = 18   # RECORDTAG
transstatus_col = 19 # TRANSSTATUS
transno_col = 14     # TRANSNO
transdate_col = 15   # TRANSDATE
divname_col = 29     # DIVNAME
```

## Keunggulan Analisis

### 1. **Fokus pada KERANI**
- Analisis khusus untuk role KERANI
- Detail setiap transaksi yang dibuat
- Tracking TRANSNO per KERANI

### 2. **Pengelompokan Divisi**
- Menampilkan struktur organisasi per divisi
- Pasangan kerja KERANI dengan MANDOR/ASISTEN
- Analisis kinerja per divisi

### 3. **Analisis Verifikasi**
- Dual verification method
- Tingkat verifikasi per KERANI
- Status verifikasi per TRANSNO

### 4. **Laporan Komprehensif**
- 4 sheet Excel dengan data lengkap
- Summary statistics
- Detail per individu dan divisi

## Contoh Use Case

### Pertanyaan Bisnis yang Dijawab:
1. **"Berapa banyak transaksi yang dibuat oleh setiap KERANI?"**
   - Lihat Sheet 2: Summary KERANI

2. **"TRANSNO apa saja yang dikerjakan oleh KERANI tertentu?"**
   - Lihat Sheet 2: kolom TRANSNO List
   - Lihat Sheet 4: Detail TRANSNO per Bulan

3. **"Siapa pasangan kerja KERANI di setiap divisi?"**
   - Lihat Sheet 3: Pengelompokan Divisi

4. **"Berapa tingkat verifikasi transaksi KERANI?"**
   - Lihat konsol output atau Sheet 2: Tingkat Verifikasi (%)

5. **"Divisi mana yang memiliki kinerja verifikasi terbaik?"**
   - Lihat Sheet 3: Tingkat Verifikasi (%) per divisi

## Troubleshooting

### Error Connection
```
❌ Koneksi database gagal!
```
**Solusi**: Pastikan path database benar dan file FDB dapat diakses

### No Data Found
```
❌ Tidak ada data transaksi untuk periode yang dipilih
```
**Solusi**: Periksa periode analisis (MONTH, YEAR) dan pastikan tabel FFBSCANNERDATA{month} ada

### No KERANI Found
```
❌ Tidak ada transaksi KERANI ditemukan
```
**Solusi**: Periksa mapping role dan pastikan ada karyawan dengan role KERANI

## File Terkait

- `analisis_detail_kerani.py` - Script utama
- `run_analisis_detail_kerani.bat` - Batch file untuk Windows
- `firebird_connector.py` - Database connector
- `analisis_per_karyawan.py` - Fungsi analisis yang digunakan
- `README_ANALISIS_DETAIL_KERANI.md` - Dokumentasi ini

---

**Dibuat oleh**: Sistem Analisis FFB IFESS  
**Versi**: 1.0  
**Tanggal**: Juni 2025  
**Tujuan**: Analisis Detail Transaksi KERANI dengan Pengelompokan Divisi dan Pasangan Kerja 