# Modular FFB Analysis System

Sistem analisis FFB (Fresh Fruit Bunch) modular yang dapat dikustomisasi dengan template yang berbeda untuk berbagai jenis laporan dan analisis.

## Struktur Proyek

```
split_by_template_report/
├── core/                           # Modul inti sistem
│   ├── __init__.py                # Ekspor kelas utama
│   ├── database_connector.py      # Koneksi database modular
│   ├── template_base.py           # Kelas dasar template
│   └── template_loader.py         # Sistem loading template dinamis
├── templates/                      # Direktori template
│   └── template_laporan_verifikasi/
│       ├── __init__.py            # Metadata template
│       ├── config.json            # Konfigurasi template
│       └── template.py            # Implementasi template
├── output/                         # Direktori output laporan
├── main_modular_ffb_analysis.py   # Aplikasi GUI utama
├── config.json                    # Konfigurasi aplikasi (auto-generated)
└── README.md                      # Dokumentasi ini
```

## Fitur Utama

### 1. Arsitektur Modular
- **Database Connector**: Modul terpisah untuk koneksi database Firebird
- **Template System**: Sistem template yang dapat dikustomisasi
- **Dynamic Loading**: Loading template secara dinamis tanpa restart aplikasi

### 2. Template System
- **Base Template**: Kelas dasar yang harus diimplementasi oleh semua template
- **Configurable**: Setiap template memiliki konfigurasi JSON terpisah
- **Extensible**: Mudah menambahkan template baru

### 3. GUI Modular
- **Tab-based Interface**: Interface berbasis tab untuk kemudahan navigasi
- **Dynamic GUI**: GUI yang berubah sesuai template yang dipilih
- **Real-time Feedback**: Log dan progress bar untuk monitoring proses

## Instalasi dan Setup

### Prerequisites
- Python 3.7+
- Tkinter (biasanya sudah terinstall dengan Python)
- Pandas
- ReportLab
- Firebird database dan isql tool

### Instalasi Dependencies
```bash
pip install pandas reportlab openpyxl
```

### Setup Database
1. Pastikan Firebird database server terinstall
2. Pastikan isql tool tersedia di PATH sistem
3. Siapkan file database (.fdb) yang akan dianalisis

## Cara Penggunaan

### 1. Menjalankan Aplikasi
```bash
python main_modular_ffb_analysis.py
```

### 2. Konfigurasi Database
1. Buka tab "Konfigurasi Database"
2. Browse dan pilih file database (.fdb)
3. Masukkan username dan password (default: SYSDBA/masterkey)
4. Klik "Test Koneksi" untuk memverifikasi
5. Klik "Load Database" untuk menginisialisasi koneksi

### 3. Memilih Template
1. Buka tab "Pilih Template"
2. Pilih template dari daftar yang tersedia
3. Lihat informasi template di panel bawah
4. Klik "Load Template" untuk mengaktifkan template

### 4. Menjalankan Analisis
1. Buka tab "Analisis"
2. Konfigurasi parameter sesuai template yang dipilih
3. Klik "Mulai Analisis" untuk memulai proses
4. Monitor progress di progress bar dan log di tab "Hasil"

### 5. Melihat Hasil
1. Buka tab "Hasil" untuk melihat log proses
2. Klik "Open Output Folder" untuk membuka folder hasil
3. File Excel dan PDF akan tersimpan di folder output

## Template Development Guide

### Membuat Template Baru

#### 1. Struktur Direktori Template
Buat direktori baru di `templates/` dengan struktur:
```
templates/nama_template_baru/
├── __init__.py
├── config.json
└── template.py
```

#### 2. File `__init__.py`
```python
"""
Template metadata
"""
__version__ = "1.0.0"
__template_name__ = "nama_template_baru"
__template_class__ = "NamaTemplateClass"

from .template import NamaTemplateClass
```

#### 3. File `config.json`
```json
{
  "name": "Nama Template Baru",
  "version": "1.0.0",
  "description": "Deskripsi template",
  "author": "Nama Author",
  "template_class": "NamaTemplateClass",
  "gui_config": {
    "default_date_range_days": 30,
    "division_selection": {
      "default_all_selected": true
    },
    "additional_filters": {
      "show_transno_filter": false
    }
  },
  "business_logic_config": {
    "verification_rules": {
      "check_data_consistency": true,
      "check_duplicate_transno": true
    },
    "analysis_options": {
      "group_by_division": true
    }
  },
  "report_config": {
    "excel_format": {
      "include_summary_sheet": true
    },
    "pdf_format": {
      "page_orientation": "landscape",
      "include_header": true
    },
    "filename_format": "Template_Baru_{timestamp}"
  },
  "sql_queries": {
    "main_query": "SELECT * FROM TRANSAKSI_FFB WHERE TANGGAL BETWEEN ? AND ? {division_filter}",
    "division_query": "SELECT DISTINCT DIVISI FROM TRANSAKSI_FFB ORDER BY DIVISI"
  },
  "validation_rules": {
    "required_columns": ["TRANSNO", "DIVISI", "TANGGAL", "BERAT_NETTO"],
    "data_types": {
      "BERAT_NETTO": "numeric",
      "TANGGAL": "datetime"
    },
    "business_rules": {
      "min_weight": 0,
      "max_weight": 50000
    }
  }
}
```

#### 4. File `template.py`
Implementasikan kelas template yang mewarisi dari `BaseTemplate`:

```python
from core.template_base import BaseTemplate, TemplateConfigInterface, TemplateGUIInterface, TemplateBusinessLogicInterface, TemplateReportInterface

class ConfigHandler(TemplateConfigInterface):
    # Implementasi handler konfigurasi
    pass

class GUIHandler(TemplateGUIInterface):
    # Implementasi handler GUI
    pass

class BusinessLogic(TemplateBusinessLogicInterface):
    # Implementasi logika bisnis
    pass

class ReportGenerator(TemplateReportInterface):
    # Implementasi generator laporan
    pass

class NamaTemplateClass(BaseTemplate):
    def __init__(self, template_name: str, template_path: str):
        super().__init__(template_name, template_path)
        # Inisialisasi template
    
    def initialize_template(self) -> bool:
        # Implementasi inisialisasi template
        pass
    
    # Implementasi method lainnya sesuai BaseTemplate
```

### Interface yang Harus Diimplementasi

#### 1. TemplateConfigInterface
- `load_config(config_path: str) -> Dict[str, Any]`
- `get_config_value(key: str, default: Any = None) -> Any`
- `validate_config() -> bool`

#### 2. TemplateGUIInterface
- `create_template_frame(parent) -> tk.Frame`
- `get_template_inputs() -> Dict[str, Any]`
- `validate_inputs() -> Tuple[bool, str]`
- `reset_inputs() -> None`

#### 3. TemplateBusinessLogicInterface
- `process_data(raw_data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame`
- `validate_data(data: pd.DataFrame) -> Tuple[bool, str]`
- `generate_summary(data: pd.DataFrame) -> Dict[str, Any]`

#### 4. TemplateReportInterface
- `generate_excel_report(data: pd.DataFrame, output_path: str, config: Dict[str, Any]) -> bool`
- `generate_pdf_report(data: pd.DataFrame, output_path: str, config: Dict[str, Any]) -> bool`
- `get_report_filename(config: Dict[str, Any]) -> str`

### Best Practices

#### 1. Konfigurasi
- Gunakan konfigurasi JSON untuk semua parameter yang dapat diubah
- Berikan nilai default untuk semua konfigurasi
- Validasi konfigurasi saat inisialisasi template

#### 2. GUI
- Buat GUI yang intuitif dan mudah digunakan
- Berikan validasi input yang jelas
- Gunakan widget yang sesuai untuk setiap jenis input

#### 3. Business Logic
- Pisahkan logika bisnis dari GUI dan database
- Implementasi validasi data yang komprehensif
- Berikan error handling yang baik

#### 4. Report Generation
- Support multiple format output (Excel, PDF)
- Berikan kustomisasi format laporan
- Implementasi error handling untuk proses pembuatan laporan

#### 5. Error Handling
- Selalu gunakan try-catch untuk operasi yang berisiko
- Berikan pesan error yang informatif
- Log semua error untuk debugging

## Template yang Tersedia

### 1. template_laporan_verifikasi
Template untuk laporan verifikasi data FFB scanner dengan fitur:
- Analisis konsistensi data berat
- Deteksi duplikasi TransNo
- Laporan per divisi
- Export Excel dan PDF
- Validasi data komprehensif

## Troubleshooting

### Database Connection Issues
1. Pastikan Firebird server berjalan
2. Periksa path database file
3. Verifikasi username/password
4. Pastikan isql tool tersedia di PATH

### Template Loading Issues
1. Periksa struktur direktori template
2. Validasi format config.json
3. Pastikan implementasi kelas template benar
4. Periksa import statement di __init__.py

### Analysis Errors
1. Periksa koneksi database
2. Validasi input parameter
3. Periksa query SQL di konfigurasi template
4. Monitor log error di tab Hasil

## Kontribusi

Untuk berkontribusi pada pengembangan sistem:
1. Fork repository
2. Buat branch untuk fitur baru
3. Implementasi fitur dengan mengikuti best practices
4. Test secara menyeluruh
5. Submit pull request

## Lisensi

Sistem ini dikembangkan untuk PT. REBINMAS JAYA. Semua hak cipta dilindungi.

## Support

Untuk bantuan teknis atau pertanyaan, hubungi tim IT PT. REBINMAS JAYA.