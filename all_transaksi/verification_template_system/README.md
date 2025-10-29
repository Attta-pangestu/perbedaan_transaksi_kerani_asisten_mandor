# Verification Template System

Sistem template modular untuk verifikasi transaksi berbasis Firebird Database (.fdb).

## Struktur Proyek

```
verification_template_system/
├── README.md                    # Dokumentasi utama
├── requirements.txt             # Dependencies Python
├── config/                      # Konfigurasi sistem
│   ├── __init__.py
│   ├── database_config.py       # Template konfigurasi database
│   └── settings.py              # Pengaturan sistem
├── templates/                   # Template verifikasi
│   ├── __init__.py
│   ├── transaction_verification.json  # Template verifikasi transaksi
│   └── base_template.json       # Template dasar
├── core/                        # Modul inti sistem
│   ├── __init__.py
│   ├── template_loader.py       # Loader template
│   ├── verification_engine.py   # Engine verifikasi
│   ├── database_connector.py    # Koneksi database
│   └── logger.py               # Sistem logging
├── utils/                       # Utilitas pendukung
│   ├── __init__.py
│   └── helpers.py              # Helper functions
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_template_loader.py
│   ├── test_verification_engine.py
│   └── test_database_connector.py
├── examples/                    # Contoh penggunaan
│   ├── __init__.py
│   └── run_transaction_verification.py
└── main.py                      # Entry point utama
```

## Fitur Utama

1. **Template Modular**: Sistem template JSON yang dapat dikustomisasi untuk berbagai jenis verifikasi
2. **Database Connector**: Koneksi Firebird yang dapat dikonfigurasi melalui template
3. **Verification Engine**: Engine verifikasi yang menggunakan template untuk menjalankan logika bisnis
4. **Logging System**: Sistem logging komprehensif untuk tracking proses verifikasi
5. **Error Handling**: Penanganan error yang robust di seluruh sistem

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Konfigurasi database di `config/database_config.py`

3. Jalankan contoh verifikasi:
```bash
python examples/run_transaction_verification.py
```

## Template Verifikasi Transaksi

Template ini diekstrak dari `gui_multi_estate_ffb_analysis.py` dan mencakup:

- Query untuk mengambil data transaksi FFB Scanner
- Logika deteksi duplikat berdasarkan TRANSNO
- Analisis perbedaan input antara Kerani, Mandor, dan Asisten
- Filter khusus TRANSSTATUS 704 untuk bulan tertentu
- Perhitungan tingkat verifikasi dan perbedaan

## Penggunaan

```python
from core.verification_engine import VerificationEngine
from config.database_config import DatabaseConfig

# Load konfigurasi database
db_config = DatabaseConfig.load_from_template()

# Inisialisasi engine verifikasi
engine = VerificationEngine(db_config)

# Jalankan verifikasi transaksi
results = engine.run_verification(
    template_name="transaction_verification",
    start_date="2025-01-01",
    end_date="2025-01-31",
    division_id="DIV001"
)
```

## Kontribusi

Sistem ini dirancang untuk mudah diperluas dengan template verifikasi baru. Untuk menambah template:

1. Buat file JSON baru di folder `templates/`
2. Definisikan queries, logika bisnis, dan parameter yang diperlukan
3. Update template loader jika diperlukan
4. Tambahkan unit tests untuk template baru