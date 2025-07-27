# Sistem Analisis FFB Multi-Estate dengan Filter TRANSSTATUS 704

## Deskripsi

Sistem analisis FFB yang telah ditingkatkan dengan implementasi filter TRANSSTATUS 704 khusus untuk **Estate 1A bulan Mei 2025**. Sistem ini menghitung perbedaan input antara Kerani dengan Mandor/Asisten berdasarkan data verifikasi yang menggunakan status transaksi 704.

## Fitur Utama

### 1. Filter TRANSSTATUS 704
- **Khusus untuk**: Estate 1A (PGE 1A) bulan Mei 2025
- **Logika**: Hanya transaksi Mandor/Asisten dengan TRANSSTATUS = 704 yang dihitung untuk perbedaan
- **Kerani**: Bisa memiliki status 704, 731, atau 732

### 2. Perhitungan Perbedaan Input
- **Field yang dibandingkan**: 
  - RIPEBCH (Buah Matang)
  - UNRIPEBCH (Buah Mentah)  
  - BLACKBCH (Buah Hitam)
  - ROTTENBCH (Buah Busuk)
  - LONGSTALKBCH (Tangkai Panjang)
  - RATDMGBCH (Kerusakan Tikus)
  - LOOSEFRUIT (Brondolan)

### 3. Prioritas Record
- **P1 (Asisten)** diprioritaskan atas **P5 (Mandor)**
- Jika ada transaksi P1 dan P5 untuk TRANSNO yang sama, P1 akan dipilih untuk perbandingan

### 4. Display Enhanced
- **Persentase Terverifikasi**: Untuk KERANI ditampilkan dengan format "88.89% (40)" 
  - Angka dalam kurung = jumlah transaksi terverifikasi
  - Warna merah untuk KERANI
- **Kolom Keterangan**: Menampilkan jumlah perbedaan input

## Cara Penggunaan

### 1. Menjalankan Sistem
```bash
# Gunakan batch file
run_enhanced_system_with_filter_704.bat

# Atau langsung dengan Python
python gui_multi_estate_ffb_analysis.py
```

### 2. Pilih Estate dan Periode
- **Estate**: Pilih "PGE 1A" untuk mengaktifkan filter TRANSSTATUS 704
- **Periode**: Pilih bulan Mei 2025 untuk filter optimal
- **Divisi**: Pilih divisi yang diinginkan atau "Semua Divisi"

### 3. Generate Report
- Klik tombol "Generate Report"
- Sistem akan menganalisis data dengan filter TRANSSTATUS 704
- Report PDF akan dihasilkan dengan informasi lengkap

## Hasil yang Diharapkan

Berdasarkan data pembanding untuk Estate 1A Mei 2025:

| Nama Kerani | Perbedaan yang Diharapkan |
|-------------|---------------------------|
| DJULI DARTA ( ADDIANI ) | 40 |
| ERLY ( MARDIAH ) | 71 |
| IRWANSYAH ( Agustina ) | 0 |
| ZULHARI ( AMINAH ) | 0 |

**Total Perbedaan Target: 111**

## File Penting

- `gui_multi_estate_ffb_analysis.py`: File utama sistem
- `test_transstatus_704_filter.py`: Script testing filter
- `LAPORAN_IMPLEMENTASI_FILTER_TRANSSTATUS_704.md`: Laporan teknis lengkap

## Troubleshooting

### 1. Hasil Tidak Sesuai Ekspektasi
- Pastikan memilih Estate "PGE 1A" 
- Pastikan periode adalah Mei 2025
- Periksa koneksi database

### 2. Error Database
- Pastikan path database benar: `C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB`
- Pastikan Firebird service berjalan
- Periksa kredensial database (sysdba/masterkey)

### 3. Performa Lambat
- Sistem memproses data dalam jumlah besar
- Tunggu hingga proses selesai
- Tutup aplikasi lain yang tidak perlu

## Kontak Support

Untuk pertanyaan atau masalah teknis, silakan hubungi tim development dengan menyertakan:
- Screenshot error (jika ada)
- Estate dan periode yang digunakan
- File log yang dihasilkan

---

**Versi**: 1.0  
**Tanggal**: Desember 2024  
**Status**: ✅ IMPLEMENTASI BERHASIL 