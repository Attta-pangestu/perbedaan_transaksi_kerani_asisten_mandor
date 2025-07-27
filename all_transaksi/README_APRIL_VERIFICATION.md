# Verifikasi Data FFB April 2025

## Overview
Dokumentasi ini menjelaskan cara memverifikasi bahwa sistem analisis FFB menghasilkan data yang sesuai dengan hasil verifikasi yang diharapkan untuk bulan April 2025.

## Data Ekspektasi (April 2025)

### Division Air Batu (A1)
- **Total Receipts**: 2,322
- **Karyawan**:
  - DJULI DARTA (ADDIANI): 381 Bunch Counter
  - ERLY (MARDIAH): 1,941 Bunch Counter  
  - SUHAYAT (ZALIAH): 314 Conductor
  - SURANTO (Nurkelumi): 281 Assistant
- **Verification Rates**:
  - Manager: 0.00%
  - Assistant: 12.10%
  - Mandore: 13.52%

### Division Air Kundo (A2)
- **Total Receipts**: 264
- **Karyawan**:
  - DJULI DARTA (ADDIANI): 141 Bunch Counter
  - ERLY (MARDIAH): 123 Bunch Counter
  - SUHAYAT (ZALIAH): 14 Conductor
  - SURANTO (Nurkelumi): 2 Assistant
- **Verification Rates**:
  - Manager: 0.00%
  - Assistant: 0.76%
  - Mandore: 5.30%

### Division Air Hijau (A3)
- **Total Receipts**: 2,008
- **Karyawan**:
  - DARWIS HERMAN: 185 Assistant
  - IRWANSYAH (Agustina): 1,199 Bunch Counter
  - ZULHARI (AMINAH): 297 Conductor, 809 Bunch Counter
- **Verification Rates**:
  - Manager: 0.00%
  - Assistant: 9.21%
  - Mandore: 14.79%

## Role Mapping yang Digunakan

Script sudah diperbaiki dengan mapping role yang benar:
- **PM** = KERANI (membuat transaksi → Bunch Counter)
- **P1** = MANDOR (memverifikasi transaksi → Conductor)
- **P5** = ASISTEN (memverifikasi transaksi → Assistant)

## Files yang Terlibat

### 1. analisis_mandor_per_divisi_corrected.py
Script utama untuk analisis mandor per divisi yang sudah diperbaiki:
- Menggunakan role mapping yang benar
- Diubah untuk analisis bulan April (month = 4)
- Menghasilkan laporan Excel dengan breakdown per divisi

### 2. test_april_data.py
Script test untuk memverifikasi data dasar April 2025:
- Test koneksi database
- Test keberadaan data di FFBScannerData04
- Breakdown per divisi dan role

### 3. verify_april_results.py
Script untuk membandingkan hasil analisis dengan data ekspektasi:
- Menjalankan analisis untuk April 2025
- Membandingkan total receipts
- Membandingkan verification rates
- Menampilkan detail per karyawan

### 4. run_test_april.bat
Batch file untuk menjalankan semua test dan analisis:
- Menjalankan test data dasar
- Menjalankan analisis utama
- Menjalankan verifikasi hasil

## Cara Menjalankan Verifikasi

### Method 1: Menggunakan Batch File
```batch
cd all_transaksi
run_test_april.bat
```

### Method 2: Menjalankan Manual
```batch
cd all_transaksi

# Test data dasar
python test_april_data.py

# Analisis utama
python analisis_mandor_per_divisi_corrected.py

# Verifikasi hasil
python verify_april_results.py
```

## Output yang Diharapkan

### 1. Test Data Dasar
- Konfirmasi koneksi database berhasil
- Jumlah total transaksi di April 2025
- Breakdown per divisi
- Breakdown per role (PM, P1, P5)

### 2. Analisis Utama
- File Excel di folder `reports/` dengan nama:
  `laporan_mandor_per_divisi_04_2025_[timestamp].xlsx`
- Sheet per divisi dengan format seperti data ekspektasi
- Summary verification rates

### 3. Verifikasi Hasil
- Perbandingan total receipts per divisi
- Perbandingan verification rates
- Status MATCH/MISMATCH untuk setiap metrik
- Detail karyawan per role

## Troubleshooting

### Database Connection Failed
- Pastikan path database benar: `C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB`
- Pastikan Firebird server berjalan
- Check firebird_connector.py untuk konfigurasi

### No Data Found
- Pastikan tabel FFBScannerData04 ada
- Pastikan ada data untuk periode April 2025
- Check tanggal format (YYYY-MM-DD)

### Verification Mismatch
- Periksa mapping divisi (ID vs Name)
- Periksa mapping karyawan (ID vs Name)
- Periksa role mapping (PM/P1/P5)
- Periksa status verifikasi (TRANSSTATUS = '704')

## Technical Notes

### Query Pattern
Script menggunakan pattern query:
```sql
FROM FFBSCANNERDATA04 a
JOIN OCFIELD b ON a.FIELDID = b.ID  
JOIN CRDIVISION c ON b.DIVID = c.ID
WHERE a.TRANSDATE >= '2025-04-01' 
AND a.TRANSDATE < '2025-05-01'
```

### Verification Logic
- Status '704' = Transaksi terverifikasi
- MANDOR verification = jumlah transaksi dengan RECORDTAG='P1' dan STATUS='704'
- ASISTEN verification = jumlah transaksi dengan RECORDTAG='P5' dan STATUS='704'
- Rate = (verified_count / total_receipts) * 100

### Column Mapping
- Column 1: SCANUSERID
- Column 18: RECORDTAG  
- Column 19: TRANSSTATUS
- Column 14: TRANSNO
- Column 15: TRANSDATE

## Expected Results
Jika sistem berjalan dengan benar, verifikasi harus menunjukkan:
- ✓ MATCH untuk total receipts (toleransi ±10)
- ✓ MATCH untuk verification rates (toleransi ±1.0%)
- Detail karyawan sesuai dengan role dan aktivitas mereka

## Contact
Jika ada masalah atau hasil tidak sesuai ekspektasi, periksa:
1. Konfigurasi database path
2. Data source periode April 2025
3. Role mapping configuration
4. Division mapping accuracy 