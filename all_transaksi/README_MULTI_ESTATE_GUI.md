# Sistem Analisis FFB Scanner Multi-Estate - GUI

## Deskripsi
Sistem analisis FFB Scanner multi-estate yang menghasilkan laporan PDF berbasis tabel sederhana untuk semua estate yang dipilih sekaligus.

## Fitur Utama

### 1. Analisis Multi-Estate
- **10 Estate**: PGE 1A, PGE 1B, PGE 2A, PGE 2B, IJL, DME, Are B2, Are B1, Are A, Are C
- **Pemilihan Fleksibel**: Pilih satu atau lebih estate untuk dianalisis
- **Date Range**: Pilih rentang tanggal analisis

### 2. Logika Verifikasi Berdasarkan Duplikat TRANSNO
- **Metode Verifikasi**: Transaksi Kerani dianggap terverifikasi jika ada transaksi dengan TRANSNO yang sama dari Mandor (P1) atau Asisten (P5)
- **Perhitungan Persentase**: % transaksi Kerani yang terverifikasi dari total yang ia buat
- **Analisis Perbedaan Input**: Menghitung jumlah field yang berbeda antara input Kerani dan Mandor/Asisten

### 3. Laporan PDF Landscape
- **Orientasi Landscape**: Menghindari cutoff tabel
- **Kolom Sederhana**: Estate, Divisi, Karyawan, Role, Jumlah Transaksi, Persentase Terverifikasi, Keterangan
- **Styling Khusus**:
  - Warna merah untuk persentase KERANI
  - Jumlah terverifikasi dalam kurung untuk KERANI
  - Background kuning untuk keterangan perbedaan input

### 4. Struktur Laporan

#### Header Kolom:
- **Estate**: Nama estate
- **Divisi**: Nama divisi
- **Karyawan**: Nama karyawan
- **Role**: KERANI, MANDOR, ASISTEN, SUMMARY
- **Jumlah Transaksi**: Total transaksi per karyawan
- **Persentase Terverifikasi**: 
  - KERANI: % terverifikasi (jumlah dalam kurung)
  - MANDOR/ASISTEN: % dari total Kerani di divisi
  - SUMMARY: % verifikasi keseluruhan divisi
- **Keterangan**: Jumlah perbedaan input untuk KERANI

#### Penjelasan Persentase:
- **KERANI**: % transaksi yang sudah diverifikasi (ada duplikat TRANSNO dengan P1/P5) dari total yang ia buat. Angka dalam kurung menunjukkan jumlah transaksi terverifikasi.
- **MANDOR/ASISTEN**: % transaksi yang ia buat per total Kerani di divisi tersebut.
- **SUMMARY**: % verifikasi keseluruhan divisi (Total Transaksi Kerani Terverifikasi / Total Transaksi Kerani).
- **GRAND TOTAL**: % verifikasi keseluruhan untuk semua estate yang dipilih.

#### Keterangan Perbedaan Input:
- Untuk setiap transaksi KERANI yang terverifikasi, sistem menghitung jumlah field yang berbeda antara input KERANI dan input MANDOR/ASISTEN.
- Field yang dibandingkan: RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT.
- Semakin banyak perbedaan, semakin besar kemungkinan ada ketidakakuratan dalam input data.

## Cara Penggunaan

### 1. Menjalankan GUI
```bash
python gui_multi_estate_ffb_analysis.py
```

### 2. Langkah-langkah:
1. **Pilih Estate**: Pilih satu atau lebih estate dari daftar
2. **Set Tanggal**: Pilih rentang tanggal analisis
3. **Klik "Mulai Analisis Multi-Estate"**
4. **Monitor Progress**: Lihat progress di log analisis
5. **Buka Hasil**: Klik "Buka Folder Output" untuk melihat PDF

### 3. File Output
- **Lokasi**: Folder `reports/`
- **Format**: `FFB_Multi_Estate_Analysis_[Bulan_Tahun]_[Timestamp].pdf`
- **Contoh**: `FFB_Multi_Estate_Analysis_April_2025_20250628_143022.pdf`

## Konfigurasi Database

### Path Database Estate:
```python
ESTATES = {
    "PGE 1A": r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB",
    "PGE 1B": r"C:\Users\nbgmf\Downloads\PTRJ_P1B\PTRJ_P1B.FDB", 
    "PGE 2A": r"C:\Users\nbgmf\Downloads\IFESS_PGE_2A_19-06-2025",
    "PGE 2B": r"C:\Users\nbgmf\Downloads\IFESS_2B_19-06-2025\PTRJ_P2B.FDB",
    "IJL": r"C:\Users\nbgmf\Downloads\IFESS_IJL_19-06-2025\PTRJ_IJL_IMPIANJAYALESTARI.FDB",
    "DME": r"C:\Users\nbgmf\Downloads\IFESS_DME_19-06-2025\PTRJ_DME.FDB",
    "Are B2": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B2_19-06-2025\PTRJ_AB2.FDB",
    "Are B1": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B1_19-06-2025\PTRJ_AB1.FDB",
    "Are A": r"C:\Users\nbgmf\Downloads\IFESS_ARE_A_19-06-2025\PTRJ_ARA.FDB",
    "Are C": r"C:\Users\nbgmf\Downloads\IFESS_ARE_C_19-06-2025\PTRJ_ARC.FDB"
}
```

## Logika Analisis

### 1. Verifikasi Transaksi
- Transaksi Kerani (RECORDTAG='PM') dianggap terverifikasi jika ada transaksi dengan TRANSNO yang sama dari Mandor (RECORDTAG='P1') atau Asisten (RECORDTAG='P5')
- Verifikasi rate = (Jumlah transaksi Kerani terverifikasi / Total transaksi Kerani) × 100%

### 2. Perbedaan Input
- Untuk setiap transaksi Kerani yang terverifikasi, sistem membandingkan nilai field antara input Kerani dan input Mandor/Asisten
- Field yang dibandingkan: RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT
- Jumlah perbedaan = jumlah field yang memiliki nilai berbeda

### 3. Perhitungan Persentase
- **KERANI**: % transaksi terverifikasi dari total yang ia buat
- **MANDOR/ASISTEN**: % transaksi yang ia buat per total Kerani di divisi
- **SUMMARY**: % verifikasi keseluruhan divisi
- **GRAND TOTAL**: % verifikasi keseluruhan semua estate

## Dependencies

### Python Packages:
- `tkinter` - GUI framework
- `tkcalendar` - Date picker
- `pandas` - Data manipulation
- `reportlab` - PDF generation
- `firebird_connector` - Database connection

### Database:
- Firebird 1.5
- Tabel FFBSCANNERDATA[MM] (MM = bulan 2 digit)
- Tabel OCFIELD, CRDIVISION, EMP

## Troubleshooting

### 1. Database Connection Error
- Periksa path database di konfigurasi ESTATES
- Pastikan Firebird server berjalan
- Periksa username/password database

### 2. No Data Found
- Periksa rentang tanggal yang dipilih
- Pastikan tabel FFBSCANNERDATA[MM] ada untuk bulan yang dipilih
- Periksa data di database untuk periode tersebut

### 3. PDF Generation Error
- Pastikan folder `reports/` dapat dibuat
- Periksa permission write di direktori
- Pastikan reportlab terinstall dengan benar

## Contoh Output

### Format PDF:
```
LAPORAN ANALISIS FFB SCANNER MULTI-ESTATE
Periode: 01 April 2025 - 30 April 2025

┌─────────┬─────────┬──────────────┬─────────┬─────────────────┬─────────────────────┬─────────────┐
│ Estate  │ Divisi  │ Karyawan     │ Role    │ Jumlah_Transaksi│ Persentase Terverif.│ Keterangan  │
├─────────┼─────────┼──────────────┼─────────┼─────────────────┼─────────────────────┼─────────────┤
│ PGE 1A  │ Air Batu│ == Air Batu  │ SUMMARY │ 150            │ 85.50%              │             │
│         │         │ TOTAL ==     │         │                 │                     │             │
├─────────┼─────────┼──────────────┼─────────┼─────────────────┼─────────────────────┼─────────────┤
│ PGE 1A  │ Air Batu│ Erly         │ KERANI  │ 45             │ 88.89% (40)         │ 12 perbedaan│
│ PGE 1A  │ Air Batu│ Mardiah      │ MANDOR  │ 35             │ 77.78%              │             │
│ PGE 1A  │ Air Batu│ Agustina     │ ASISTEN │ 30             │ 66.67%              │             │
└─────────┴─────────┴──────────────┴─────────┴─────────────────┴─────────────────────┴─────────────┘
```

## Versi Terbaru
- **v2.0**: Menambahkan analisis perbedaan input
- **v1.5**: Landscape PDF dan styling khusus
- **v1.0**: Sistem multi-estate dasar 