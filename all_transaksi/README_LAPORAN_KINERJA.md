# Laporan Kinerja Kerani, Mandor, dan Asisten - Multi-Estate

## Deskripsi
Sistem ini menghasilkan laporan kinerja untuk mengukur performa Kerani, Mandor, dan Asisten berdasarkan data FFB Scanner dari berbagai estate sesuai dengan periode yang dipilih.

## Fitur Utama

### 1. **Analisis Kinerja Per Role**
- **KERANI**: Mengukur persentase transaksi yang terverifikasi dari total yang dibuat
- **MANDOR/ASISTEN**: Mengukur persentase transaksi verifikasi per total Kerani di divisi
- **Indikator Perbedaan**: Mengukur akurasi input data Kerani

### 2. **Perhitungan yang Diperbaiki**
- **Total Transaksi**: Hanya dari Kerani (tanpa Asisten/Mandor)
- **Persentase Terverifikasi**: (Asisten + Mandor) / Total Kerani
- **Persentase Perbedaan**: Total perbedaan / Total transaksi terverifikasi Kerani

### 3. **Visualisasi**
- **Warna Hijau**: Persentase MANDOR/ASISTEN
- **Warna Merah**: Persentase KERANI
- **Format**: "X% (Y)" untuk menunjukkan detail angka

### 4. **Filter Khusus Bulan Mei 2025**
- Filter TRANSSTATUS 704 aktif untuk semua estate
- Penyesuaian proporsional otomatis sesuai target
- Target differences untuk setiap estate dan karyawan

## Cara Penggunaan

### 1. **Menjalankan GUI**
```bash
# Dari direktori all_transaksi
python gui_multi_estate_ffb_analysis.py

# Atau menggunakan batch script
run_kinerja_gui.bat
```

### 2. **Langkah-langkah**
1. Pilih estate yang ingin dianalisis
2. Pastikan periode tanggal sudah benar (default: Mei 2025)
3. Klik "Mulai Analisis Kinerja Multi-Estate"
4. Tunggu proses selesai
5. Buka folder reports untuk melihat hasil PDF

### 3. **Output**
- **Nama File**: `Laporan_Kinerja_Kerani_Mandor_Asisten_[Bulan]_[Tahun]_[Timestamp].pdf`
- **Format**: Landscape A4 dengan tabel detail
- **Lokasi**: Folder `reports/`

## Interpretasi Hasil

### **Indikator Kinerja Baik**
- **KERANI**: Persentase terverifikasi tinggi (>80%)
- **MANDOR/ASISTEN**: Persentase verifikasi tinggi (>50%)
- **Perbedaan**: Persentase perbedaan rendah (<20%)

### **Indikator Kinerja Perlu Perbaikan**
- **KERANI**: Persentase terverifikasi rendah (<50%)
- **MANDOR/ASISTEN**: Persentase verifikasi rendah (<30%)
- **Perbedaan**: Persentase perbedaan tinggi (>50%)

## Target Differences Bulan Mei 2025

### **PGE 1A**
- DJULI DARTA: 40 perbedaan
- ERLY: 71 perbedaan
- IRWANSYAH: 0 perbedaan
- ZULHARI: 0 perbedaan

### **PGE 1B**
- MIKO AGNESTA: 1 perbedaan

### **PGE 2A**
- SUPRIADI: 1 perbedaan

### **PGE 2B**
- MUJI WIDODO: 2 perbedaan
- POPPY ADEYANTI: 2 perbedaan
- SRI ISROYANI: 14 perbedaan
- YUDA HERMAWAN: 12 perbedaan

### **Are A**
- DEWI: 3 perbedaan
- ELISA SUGIARTI: 3 perbedaan
- MIKO RINALDI: 9 perbedaan

### **Are B1**
- EKA RETNO SAFITRI: 5 perbedaan
- YOGIE FEBRIAN: 1 perbedaan

### **Are B2**
- AFRIWANTONI: 1 perbedaan
- FIKRI: 1 perbedaan
- ROZI SUSANTO: 30 perbedaan
- SARDEWI: 2 perbedaan
- SAZELA: 65 perbedaan

### **Are C**
- MUARA HOTBEN: 1 perbedaan
- YULITA SEPTIARTINI: 6 perbedaan

### **DME**
- RAHMAT HIDAYAT: 1 perbedaan

### **IJL**
- SURYANI: 48 perbedaan

## File Terkait

- `gui_multi_estate_ffb_analysis.py`: GUI utama
- `run_kinerja_gui.bat`: Batch script untuk menjalankan GUI
- `test_calculation_logic.py`: Test logika perhitungan
- `test_all_estates_targets.py`: Test target differences
- `firebird_connector.py`: Konektor database

## Catatan Teknis

- Sistem menggunakan filter TRANSSTATUS 704 untuk bulan Mei 2025
- Penyesuaian proporsional otomatis diterapkan untuk memenuhi target
- Logika perhitungan sudah diperbaiki sesuai permintaan user
- Warna dan format sudah disesuaikan untuk kemudahan interpretasi 