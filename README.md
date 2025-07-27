# Analisis Perbedaan Data Panen Ifess

Program untuk menganalisis database Firebird Ifess dan membuat laporan perbedaan data panen antara Kerani dan Asisten. Program ini juga menyediakan mapping antara FieldID dan FieldNo dari tabel OCFIELD.

## Fitur

- Koneksi ke database Firebird menggunakan isql
- Analisis perbedaan data panen pada transaksi dengan TRANSNO yang sama
- Perhitungan perbedaan pada kolom RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT
- Mapping FieldID dengan FieldNo dari tabel OCFIELD
- Mapping ScanUserID dengan nama karyawan dari tabel EMP
- Hanya menampilkan transaksi yang memiliki perbedaan nilai
- Pembuatan laporan dalam format Excel
- Visualisasi data dengan grafik

## Persyaratan

- Python 3.7 atau lebih baru
- Firebird 1.5
- Paket Python yang diperlukan:
  - pandas
  - matplotlib
  - openpyxl

## Instalasi

1. Pastikan Python dan Firebird sudah terinstal
2. Instal paket yang diperlukan:

```
pip install pandas matplotlib openpyxl
```

## Penggunaan

Jalankan program dengan perintah:

```
python analisis_perbedaan_panen.py
```

### Parameter Opsional

- `--db-path`: Path ke file database Firebird (default: "D:\Gawean Rebinmas\Monitoring Database\Database Ifess\PTRJ_P1A_08042025\PTRJ_P1A.FDB")
- `--isql-path`: Path ke executable isql (default: "C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe")
- `--username`: Username database (default: 'sysdba')
- `--password`: Password database (default: 'masterkey')
- `--start-date`: Tanggal mulai untuk analisis (format: YYYY-MM-DD, default: '2025-03-01')
- `--end-date`: Tanggal akhir untuk analisis (format: YYYY-MM-DD, default: '2025-04-01')
- `--output-dir`: Direktori untuk menyimpan laporan (default: 'reports')
- `--use-localhost`: Gunakan format localhost:path untuk koneksi (default: False)
- `--limit`: Batasan jumlah TRANSNO yang dianalisis (default: 100)

Contoh:

```
python analisis_perbedaan_panen.py --start-date 2025-02-01 --end-date 2025-03-01 --use-localhost --limit 50
```

## Output

Program akan menghasilkan:

1. Preview analisis di konsol
2. File Excel dengan hasil analisis detail dan ringkasan statistik
3. File gambar dengan grafik visualisasi data

Semua file output disimpan di direktori 'reports' (atau direktori yang ditentukan dengan parameter `--output-dir`).

## Struktur Proyek

- `analisis_perbedaan_panen.py`: File utama aplikasi
- `firebird_connector.py`: Modul untuk koneksi database Firebird
- `README.md`: Dokumentasi proyek

## Penjelasan Analisis

Program ini menganalisis perbedaan data panen antara Kerani dan Asisten dengan langkah-langkah berikut:

1. Mendapatkan mapping antara FieldID dan FieldNo dari tabel OCFIELD
2. Mendapatkan mapping antara ScanUserID dan nama karyawan dari tabel EMP
3. Mencari transaksi dengan TRANSNO yang sama (duplikat)
4. Untuk setiap TRANSNO duplikat, membandingkan nilai pada kolom-kolom berikut:
   - RIPEBCH (Buah Matang)
   - UNRIPEBCH (Buah Mentah)
   - BLACKBCH (Buah Hitam)
   - ROTTENBCH (Buah Busuk)
   - LONGSTALKBCH (Buah Tangkai Panjang)
   - RATDMGBCH (Buah Rusak Tikus)
   - LOOSEFRUIT (Brondolan)
5. Menghitung perbedaan nilai untuk setiap kolom
6. Memfilter hanya transaksi yang memiliki perbedaan nilai
7. Menghasilkan statistik ringkasan dan visualisasi

## Troubleshooting

Jika mengalami masalah koneksi database:

1. Pastikan path database dan isql benar
2. Coba gunakan opsi `--use-localhost` untuk format koneksi alternatif
3. Periksa apakah username dan password benar
4. Pastikan database tidak sedang digunakan oleh aplikasi lain
