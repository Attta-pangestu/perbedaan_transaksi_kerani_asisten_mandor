# API Reference - Verification Template System

## Daftar Isi
1. [Config Module](#config-module)
2. [Templates Module](#templates-module)
3. [Core Module](#core-module)
4. [Utilities](#utilities)

## Config Module

### DatabaseConfig

Kelas untuk mengelola konfigurasi database Firebird.

#### Constructor

```python
DatabaseConfig(database_path: Union[str, Path], estate_name: str = "default")
```

**Parameters:**
- `database_path`: Path ke file database (.fdb)
- `estate_name`: Nama estate (default: "default")

#### Methods

##### `load_from_config(config_path: Union[str, Path]) -> DatabaseConfig`

Load konfigurasi database dari file JSON.

**Parameters:**
- `config_path`: Path ke file config.json

**Returns:**
- `DatabaseConfig`: Instance konfigurasi database

**Example:**
```python
db_config = DatabaseConfig.load_from_config("config.json")
```

##### `create_template_config(output_path: Union[str, Path])`

Buat template file konfigurasi.

**Parameters:**
- `output_path`: Path output file template

**Example:**
```python
DatabaseConfig.create_template_config("new_config.json")
```

##### `get_connection_string() -> str`

Dapatkan connection string untuk database.

**Returns:**
- `str`: Connection string

##### `test_connection() -> bool`

Test koneksi ke database.

**Returns:**
- `bool`: True jika koneksi berhasil

##### `validate_database_path() -> bool`

Validasi path database.

**Returns:**
- `bool`: True jika path valid

### Settings

Kelas untuk mengelola pengaturan sistem.

#### Properties

- `TEMPLATES_DIR`: Path direktori templates
- `LOGS_DIR`: Path direktori logs
- `REPORTS_DIR`: Path direktori reports
- `DATABASE_TIMEOUT`: Timeout koneksi database
- `BATCH_SIZE`: Ukuran batch default
- `MAX_RETRY_ATTEMPTS`: Maksimal retry attempts

#### Methods

##### `ensure_directories()`

Pastikan semua direktori yang diperlukan ada.

##### `get_template_path(template_name: str) -> Path`

Dapatkan path template berdasarkan nama.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `Path`: Path ke template

##### `get_log_path(log_name: str) -> Path`

Dapatkan path log file.

**Parameters:**
- `log_name`: Nama log file

**Returns:**
- `Path`: Path ke log file

## Templates Module

### TransactionVerificationTemplate

Template untuk verifikasi transaksi FFB.

#### Constructor

```python
TransactionVerificationTemplate(template_config: dict, db_config: DatabaseConfig)
```

**Parameters:**
- `template_config`: Konfigurasi template dari JSON
- `db_config`: Konfigurasi database

#### Methods

##### `run_verification(estate_name: str, start_date: str, end_date: str) -> dict`

Jalankan verifikasi untuk estate dan rentang tanggal tertentu.

**Parameters:**
- `estate_name`: Nama estate
- `start_date`: Tanggal mulai (YYYY-MM-DD)
- `end_date`: Tanggal akhir (YYYY-MM-DD)

**Returns:**
- `dict`: Hasil verifikasi

**Example:**
```python
result = template.run_verification("PGE 2B", "2024-01-01", "2024-01-31")
```

##### `connect_database() -> fdb.Connection`

Buat koneksi ke database.

**Returns:**
- `fdb.Connection`: Koneksi database

##### `get_employee_mapping(conn: fdb.Connection, estate_name: str) -> dict`

Dapatkan mapping employee ID ke nama.

**Parameters:**
- `conn`: Koneksi database
- `estate_name`: Nama estate

**Returns:**
- `dict`: Mapping employee ID ke nama

##### `get_divisions(conn: fdb.Connection, estate_name: str, start_date: str, end_date: str) -> List[str]`

Dapatkan daftar divisi untuk rentang tanggal.

**Parameters:**
- `conn`: Koneksi database
- `estate_name`: Nama estate
- `start_date`: Tanggal mulai
- `end_date`: Tanggal akhir

**Returns:**
- `List[str]`: Daftar nama divisi

##### `analyze_division(conn: fdb.Connection, division: str, estate_name: str) -> dict`

Analisis data untuk satu divisi.

**Parameters:**
- `conn`: Koneksi database
- `division`: Nama divisi
- `estate_name`: Nama estate

**Returns:**
- `dict`: Hasil analisis divisi

## Core Module

### TemplateLoader

Kelas untuk memuat template verifikasi.

#### Constructor

```python
TemplateLoader(templates_dir: Optional[Union[str, Path]] = None)
```

**Parameters:**
- `templates_dir`: Direktori templates (optional)

#### Methods

##### `get_available_templates() -> List[str]`

Dapatkan daftar template yang tersedia.

**Returns:**
- `List[str]`: Daftar nama template

##### `get_template_info(template_name: str) -> dict`

Dapatkan informasi template.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `dict`: Informasi template

##### `load_template_config(template_name: str) -> dict`

Load konfigurasi template dari JSON.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `dict`: Konfigurasi template

##### `load_template_class(template_name: str) -> type`

Load kelas template.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `type`: Kelas template

##### `create_template_instance(template_name: str, db_config: DatabaseConfig) -> object`

Buat instance template.

**Parameters:**
- `template_name`: Nama template
- `db_config`: Konfigurasi database

**Returns:**
- `object`: Instance template

##### `validate_template(template_name: str) -> bool`

Validasi template.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `bool`: True jika template valid

### VerificationEngine

Engine utama untuk menjalankan verifikasi.

#### Constructor

```python
VerificationEngine(db_config: Optional[DatabaseConfig] = None, 
                  templates_dir: Optional[Union[str, Path]] = None,
                  verbose: bool = False)
```

**Parameters:**
- `db_config`: Konfigurasi database (optional)
- `templates_dir`: Direktori templates (optional)
- `verbose`: Enable verbose logging

#### Methods

##### `get_available_templates() -> List[str]`

Dapatkan daftar template yang tersedia.

**Returns:**
- `List[str]`: Daftar nama template

##### `load_template(template_name: str) -> object`

Load template berdasarkan nama.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `object`: Instance template

##### `validate_template(template_name: str) -> bool`

Validasi template.

**Parameters:**
- `template_name`: Nama template

**Returns:**
- `bool`: True jika template valid

##### `run_verification(template_name: str, estate_name: str, start_date: str, end_date: str, custom_config: Optional[dict] = None) -> dict`

Jalankan verifikasi.

**Parameters:**
- `template_name`: Nama template
- `estate_name`: Nama estate
- `start_date`: Tanggal mulai
- `end_date`: Tanggal akhir
- `custom_config`: Konfigurasi custom (optional)

**Returns:**
- `dict`: Hasil verifikasi

**Example:**
```python
result = engine.run_verification(
    "transaction_verification",
    "PGE 2B",
    "2024-01-01",
    "2024-01-31"
)
```

##### `save_results(results: dict, output_path: Union[str, Path])`

Simpan hasil verifikasi ke file.

**Parameters:**
- `results`: Hasil verifikasi
- `output_path`: Path output file

##### `cleanup()`

Bersihkan resources.

### VerificationBatch

Kelas untuk menjalankan batch verifikasi.

#### Constructor

```python
VerificationBatch(engine: Optional[VerificationEngine] = None)
```

**Parameters:**
- `engine`: Instance VerificationEngine (optional)

#### Methods

##### `add_job(template_name: str, estate_name: str, start_date: str, end_date: str, custom_config: Optional[dict] = None) -> str`

Tambah job ke batch.

**Parameters:**
- `template_name`: Nama template
- `estate_name`: Nama estate
- `start_date`: Tanggal mulai
- `end_date`: Tanggal akhir
- `custom_config`: Konfigurasi custom (optional)

**Returns:**
- `str`: Job ID

##### `remove_job(job_id: str) -> bool`

Hapus job dari batch.

**Parameters:**
- `job_id`: ID job

**Returns:**
- `bool`: True jika berhasil

##### `get_jobs() -> List[dict]`

Dapatkan daftar jobs.

**Returns:**
- `List[dict]`: Daftar jobs

##### `run_all() -> List[dict]`

Jalankan semua jobs.

**Returns:**
- `List[dict]`: Hasil semua jobs

##### `run_job(job_id: str) -> dict`

Jalankan job tertentu.

**Parameters:**
- `job_id`: ID job

**Returns:**
- `dict`: Hasil job

### VerificationLogger

Logger khusus untuk sistem verifikasi.

#### Constructor

```python
VerificationLogger(name: str = "verification_system",
                  log_level: Union[str, int] = logging.INFO,
                  enable_file_logging: bool = True,
                  enable_console_logging: bool = True)
```

**Parameters:**
- `name`: Nama logger
- `log_level`: Level logging
- `enable_file_logging`: Enable file logging
- `enable_console_logging`: Enable console logging

#### Methods

##### `start_verification_session(session_info: Dict[str, Any])`

Mulai session verifikasi.

**Parameters:**
- `session_info`: Informasi session

##### `end_verification_session(session_result: Dict[str, Any])`

Akhiri session verifikasi.

**Parameters:**
- `session_result`: Hasil session

##### `log_verification_step(step_name: str, step_data: Dict[str, Any], level: int = logging.INFO)`

Log step verifikasi.

**Parameters:**
- `step_name`: Nama step
- `step_data`: Data step
- `level`: Level logging

##### `log_database_operation(operation: str, query: str, params: Optional[Dict] = None, result_count: Optional[int] = None, duration: Optional[float] = None)`

Log operasi database.

**Parameters:**
- `operation`: Jenis operasi
- `query`: Query SQL
- `params`: Parameter query
- `result_count`: Jumlah hasil
- `duration`: Durasi eksekusi

##### `log_template_operation(template_name: str, operation: str, details: Dict[str, Any])`

Log operasi template.

**Parameters:**
- `template_name`: Nama template
- `operation`: Jenis operasi
- `details`: Detail operasi

##### `log_error_with_context(error: Exception, context: Dict[str, Any])`

Log error dengan context.

**Parameters:**
- `error`: Exception
- `context`: Context error

##### `get_session_logs() -> List[Dict[str, Any]]`

Dapatkan log session.

**Returns:**
- `List[Dict[str, Any]]`: Log session

##### `export_session_logs(output_path: Optional[Union[str, Path]] = None) -> Optional[str]`

Export log session.

**Parameters:**
- `output_path`: Path output (optional)

**Returns:**
- `Optional[str]`: Path file yang di-export

## Utilities

### setup_logging

Setup logging untuk aplikasi.

```python
setup_logging(log_level: Union[str, int] = logging.INFO,
             enable_file_logging: bool = True,
             enable_console_logging: bool = True) -> VerificationLogger
```

**Parameters:**
- `log_level`: Level logging
- `enable_file_logging`: Enable file logging
- `enable_console_logging`: Enable console logging

**Returns:**
- `VerificationLogger`: Instance logger

### get_logger

Dapatkan logger dengan nama tertentu.

```python
get_logger(name: str) -> logging.Logger
```

**Parameters:**
- `name`: Nama logger

**Returns:**
- `logging.Logger`: Instance logger

## Error Handling

### Exception Classes

#### `TemplateNotFoundError`

Raised ketika template tidak ditemukan.

#### `DatabaseConnectionError`

Raised ketika koneksi database gagal.

#### `TemplateValidationError`

Raised ketika validasi template gagal.

#### `VerificationError`

Raised ketika proses verifikasi gagal.

### Error Response Format

Semua method yang mengembalikan dict akan menggunakan format berikut untuk error:

```python
{
    'success': False,
    'error': 'Error message',
    'error_type': 'ErrorClassName',
    'context': {
        # Additional context information
    }
}
```

### Success Response Format

Format untuk response sukses:

```python
{
    'success': True,
    'data': {
        # Response data
    },
    'metadata': {
        'timestamp': '2024-01-01T12:00:00',
        'execution_time': 1.23,
        'template_name': 'transaction_verification'
    }
}
```

## Configuration Schema

### Template JSON Schema

```json
{
    "template_info": {
        "name": "string",
        "version": "string",
        "description": "string",
        "author": "string",
        "created_date": "string",
        "last_modified": "string"
    },
    "database_queries": {
        "employee_mapping": "string",
        "division_tables": "string",
        "granular_data": "string"
    },
    "business_logic": {
        "duplicate_handling": {
            "group_by_fields": ["string"],
            "aggregate_fields": ["string"]
        },
        "calculations": {
            "kerani_data": {
                "filter_condition": "string",
                "special_filters": [
                    {
                        "condition": "string",
                        "estates": ["string"],
                        "months": ["string"]
                    }
                ]
            }
        }
    },
    "output_format": {
        "fields": ["string"],
        "summary_fields": ["string"]
    },
    "configuration": {
        "batch_size": "integer",
        "timeout_seconds": "integer",
        "retry_attempts": "integer"
    }
}
```

### Database Config Schema

```json
{
    "estate_name": "path/to/database.fdb"
}
```

## Examples

### Complete Usage Example

```python
from verification_template_system.core import VerificationEngine, setup_logging
from verification_template_system.config.database_config import DatabaseConfig

# Setup
logger = setup_logging()
db_config = DatabaseConfig.load_from_config("config.json")
engine = VerificationEngine(db_config=db_config)

# Run verification
result = engine.run_verification(
    template_name="transaction_verification",
    estate_name="PGE 2B",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Handle result
if result['success']:
    print("Verification completed successfully!")
    engine.save_results(result, "results.json")
else:
    print(f"Verification failed: {result['error']}")
```

### Batch Processing Example

```python
from verification_template_system.core.verification_engine import VerificationBatch

batch = VerificationBatch()

# Add multiple jobs
batch.add_job("transaction_verification", "PGE 2B", "2024-01-01", "2024-01-31")
batch.add_job("transaction_verification", "PGE 2C", "2024-01-01", "2024-01-31")

# Run all jobs
results = batch.run_all()

for result in results:
    print(f"Job {result['job_id']}: {'Success' if result['success'] else 'Failed'}")
```

### Custom Template Example

```python
from verification_template_system.templates.base_template import BaseVerificationTemplate

class CustomTemplate(BaseVerificationTemplate):
    def run_verification(self, estate_name: str, start_date: str, end_date: str) -> dict:
        try:
            # Custom implementation
            return {'success': True, 'data': {}}
        except Exception as e:
            return {'success': False, 'error': str(e)}
```