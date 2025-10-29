# Panduan Implementasi Verification Template System

## Daftar Isi
1. [Pengenalan](#pengenalan)
2. [Instalasi dan Setup](#instalasi-dan-setup)
3. [Konfigurasi Database](#konfigurasi-database)
4. [Membuat Template Verifikasi](#membuat-template-verifikasi)
5. [Menggunakan Template System](#menggunakan-template-system)
6. [Logging dan Monitoring](#logging-dan-monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Pengenalan

Verification Template System adalah sistem modular yang memungkinkan Anda untuk:
- Memisahkan logika verifikasi dari kode aplikasi
- Membuat template verifikasi yang dapat digunakan kembali
- Mengelola konfigurasi database secara terpusat
- Melakukan logging dan monitoring yang komprehensif

### Arsitektur Sistem

```
verification_template_system/
├── config/                 # Konfigurasi sistem
│   ├── database_config.py  # Konfigurasi database
│   └── settings.py         # Pengaturan sistem
├── templates/              # Template verifikasi
│   ├── transaction_verification.json
│   └── transaction_verification.py
├── core/                   # Komponen inti
│   ├── template_loader.py  # Loader template
│   ├── verification_engine.py  # Engine verifikasi
│   └── logging_config.py   # Konfigurasi logging
└── docs/                   # Dokumentasi
```

## Instalasi dan Setup

### 1. Persiapan Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable (opsional)
set VERIFICATION_ENV=development
```

### 2. Struktur Direktori

Pastikan struktur direktori sesuai dengan yang diharapkan:

```python
from verification_template_system.config.settings import Settings

settings = Settings()
print(f"Templates directory: {settings.TEMPLATES_DIR}")
print(f"Logs directory: {settings.LOGS_DIR}")
print(f"Reports directory: {settings.REPORTS_DIR}")
```

## Konfigurasi Database

### 1. Setup Database Configuration

Buat file `config.json` di root directory:

```json
{
    "PGE 2B": "D:/Path/To/Your/Database/PTRJ_P2B.FDB"
}
```

### 2. Menggunakan Database Config

```python
from verification_template_system.config.database_config import DatabaseConfig

# Load konfigurasi
db_config = DatabaseConfig.load_from_config("config.json")

# Dapatkan connection string
conn_string = db_config.get_connection_string()
print(f"Database: {conn_string}")

# Test koneksi
if db_config.test_connection():
    print("Database connection successful!")
else:
    print("Database connection failed!")
```

### 3. Membuat Template Database Config

```python
# Buat template config baru
DatabaseConfig.create_template_config("new_config.json")
```

## Membuat Template Verifikasi

### 1. Struktur Template JSON

Template JSON mendefinisikan konfigurasi dan metadata:

```json
{
    "template_info": {
        "name": "my_verification_template",
        "version": "1.0.0",
        "description": "Template untuk verifikasi custom",
        "author": "Your Name",
        "created_date": "2024-01-01",
        "last_modified": "2024-01-01"
    },
    "database_queries": {
        "employee_mapping": "SELECT EMP_ID, EMP_NAME FROM EMP WHERE ESTATE = ?",
        "division_tables": "SELECT DISTINCT DIVISION FROM FFBSCANNERDATA_{date} WHERE ESTATE = ?",
        "granular_data": "SELECT * FROM FFBSCANNERDATA_{table} WHERE DIVISION = ? AND ESTATE = ?"
    },
    "business_logic": {
        "duplicate_handling": {
            "group_by_fields": ["TRANSNO", "DIVISION"],
            "aggregate_fields": ["RIPEBCH", "UNRIPEBCH", "EMPTYBNCH"]
        },
        "calculations": {
            "kerani_data": {
                "filter_condition": "duplicate_count > 1",
                "special_filters": [
                    {
                        "condition": "TRANSSTATUS == 704",
                        "estates": ["PGE 2B"],
                        "months": ["10", "11", "12"]
                    }
                ]
            }
        }
    },
    "output_format": {
        "fields": ["employee_name", "kerani_total", "mandor_total", "asisten_total"],
        "summary_fields": ["total_employees", "verification_rate"]
    }
}
```

### 2. Implementasi Template Python

```python
from verification_template_system.templates.base_template import BaseVerificationTemplate

class MyVerificationTemplate(BaseVerificationTemplate):
    def __init__(self, template_config: dict, db_config):
        super().__init__(template_config, db_config)
    
    def run_verification(self, estate_name: str, start_date: str, end_date: str) -> dict:
        """
        Implementasi logika verifikasi custom.
        """
        try:
            # 1. Connect to database
            conn = self.connect_database()
            
            # 2. Get employee mapping
            employees = self.get_employee_mapping(conn, estate_name)
            
            # 3. Process divisions
            results = {}
            divisions = self.get_divisions(conn, estate_name, start_date, end_date)
            
            for division in divisions:
                division_result = self.analyze_division(conn, division, estate_name)
                results[division] = division_result
            
            # 4. Generate summary
            summary = self.generate_summary(results)
            
            return {
                'success': True,
                'estate_name': estate_name,
                'results': results,
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if 'conn' in locals():
                conn.close()
    
    def analyze_division(self, conn, division: str, estate_name: str) -> dict:
        """
        Implementasi analisis per divisi.
        """
        # Custom logic here
        pass
```

### 3. Registrasi Template

Template akan otomatis terdeteksi jika ditempatkan di direktori `templates/` dengan naming convention yang benar.

## Menggunakan Template System

### 1. Basic Usage

```python
from verification_template_system.core import VerificationEngine, setup_logging

# Setup logging
logger = setup_logging()

# Initialize engine
engine = VerificationEngine()

# Load template
template = engine.load_template("transaction_verification")

# Run verification
result = engine.run_verification(
    template_name="transaction_verification",
    estate_name="PGE 2B",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

print(f"Verification result: {result}")
```

### 2. Advanced Usage dengan Custom Parameters

```python
# Load template dengan custom config
custom_config = {
    'batch_size': 1000,
    'enable_special_filters': True,
    'output_format': 'detailed'
}

result = engine.run_verification(
    template_name="transaction_verification",
    estate_name="PGE 2B",
    start_date="2024-01-01",
    end_date="2024-01-31",
    custom_config=custom_config
)
```

### 3. Batch Processing

```python
from verification_template_system.core.verification_engine import VerificationBatch

# Setup batch job
batch = VerificationBatch()

# Add multiple jobs
batch.add_job("transaction_verification", "PGE 2B", "2024-01-01", "2024-01-31")
batch.add_job("transaction_verification", "PGE 2C", "2024-01-01", "2024-01-31")

# Run batch
results = batch.run_all()

for result in results:
    print(f"Job {result['job_id']}: {result['status']}")
```

## Logging dan Monitoring

### 1. Setup Logging

```python
from verification_template_system.core import setup_logging

# Basic setup
logger = setup_logging(
    log_level="INFO",
    enable_file_logging=True,
    enable_console_logging=True
)
```

### 2. Verification Session Tracking

```python
# Start session
session_info = {
    'template_name': 'transaction_verification',
    'estate_name': 'PGE 2B',
    'start_date': '2024-01-01',
    'end_date': '2024-01-31'
}

logger.start_verification_session(session_info)

# Log steps
logger.log_verification_step("database_connection", {
    'message': 'Connecting to database',
    'database_path': '/path/to/database.fdb'
})

logger.log_verification_step("data_processing", {
    'message': 'Processing divisions',
    'division_count': 5
})

# End session
session_result = {
    'success': True,
    'total_records': 1500,
    'processing_time': 45.2
}

logger.end_verification_session(session_result)
```

### 3. Export Session Logs

```python
# Export current session logs
export_path = logger.export_session_logs()
print(f"Logs exported to: {export_path}")

# Export to specific path
export_path = logger.export_session_logs("custom_logs.json")
```

### 4. Database Operation Logging

```python
# Log database operations
logger.log_database_operation(
    operation="SELECT",
    query="SELECT * FROM EMP WHERE ESTATE = ?",
    params={'estate': 'PGE 2B'},
    result_count=150,
    duration=0.245
)
```

## Troubleshooting

### 1. Common Issues

#### Database Connection Failed
```python
# Check database path
db_config = DatabaseConfig.load_from_config("config.json")
print(f"Database path: {db_config.database_path}")
print(f"Path exists: {db_config.database_path.exists()}")

# Test connection
if not db_config.test_connection():
    print("Database connection failed!")
    # Check firebird service, file permissions, etc.
```

#### Template Not Found
```python
# List available templates
engine = VerificationEngine()
templates = engine.get_available_templates()
print(f"Available templates: {templates}")

# Check template directory
from verification_template_system.config.settings import Settings
settings = Settings()
print(f"Templates directory: {settings.TEMPLATES_DIR}")
print(f"Directory exists: {settings.TEMPLATES_DIR.exists()}")
```

#### Memory Issues dengan Large Dataset
```python
# Adjust batch size
custom_config = {
    'batch_size': 500,  # Reduce from default 1000
    'enable_chunked_processing': True
}

result = engine.run_verification(
    template_name="transaction_verification",
    estate_name="PGE 2B",
    start_date="2024-01-01",
    end_date="2024-01-31",
    custom_config=custom_config
)
```

### 2. Debug Mode

```python
# Enable debug logging
logger = setup_logging(log_level="DEBUG")

# Enable verbose output
engine = VerificationEngine(verbose=True)
```

### 3. Log Analysis

```python
# Analyze session logs
import json

with open("session_logs.json", 'r') as f:
    logs = json.load(f)

# Find errors
errors = [log for log in logs['logs'] if 'error' in log.get('step_data', {})]
print(f"Found {len(errors)} errors")

# Performance analysis
durations = [log['step_data'].get('duration', 0) for log in logs['logs']]
avg_duration = sum(durations) / len(durations)
print(f"Average step duration: {avg_duration:.2f}s")
```

## Best Practices

### 1. Template Design

- **Modular**: Pisahkan logika bisnis ke dalam method-method kecil
- **Configurable**: Gunakan template JSON untuk parameter yang sering berubah
- **Error Handling**: Selalu handle exception dengan proper logging
- **Documentation**: Dokumentasikan setiap method dan parameter

```python
class MyTemplate(BaseVerificationTemplate):
    def run_verification(self, estate_name: str, start_date: str, end_date: str) -> dict:
        """
        Run verification for specified estate and date range.
        
        Args:
            estate_name: Name of the estate to verify
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            dict: Verification results with success status
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            self.logger.log_error_with_context(e, {
                'estate_name': estate_name,
                'start_date': start_date,
                'end_date': end_date
            })
            return {'success': False, 'error': str(e)}
```

### 2. Performance Optimization

- **Connection Pooling**: Reuse database connections
- **Batch Processing**: Process data in chunks
- **Caching**: Cache frequently accessed data
- **Indexing**: Ensure proper database indexing

```python
# Example: Batch processing
def process_divisions_batch(self, divisions: List[str], batch_size: int = 100):
    """Process divisions in batches to optimize memory usage."""
    for i in range(0, len(divisions), batch_size):
        batch = divisions[i:i + batch_size]
        yield self.process_division_batch(batch)
```

### 3. Error Handling

```python
def safe_database_operation(self, operation_func, *args, **kwargs):
    """
    Safely execute database operation with retry logic.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            self.logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
            time.sleep(1)  # Wait before retry
```

### 4. Testing

```python
# Unit test example
import unittest
from verification_template_system.templates.transaction_verification import TransactionVerificationTemplate

class TestTransactionVerification(unittest.TestCase):
    def setUp(self):
        self.template_config = {...}  # Load test config
        self.db_config = {...}  # Load test db config
        self.template = TransactionVerificationTemplate(self.template_config, self.db_config)
    
    def test_employee_mapping(self):
        """Test employee mapping retrieval."""
        # Mock database connection
        # Test the method
        # Assert results
        pass
    
    def test_division_analysis(self):
        """Test division analysis logic."""
        # Test with sample data
        pass
```

### 5. Monitoring dan Maintenance

- **Regular Log Review**: Review logs untuk identify patterns
- **Performance Monitoring**: Track execution times dan resource usage
- **Database Maintenance**: Regular database optimization
- **Template Updates**: Keep templates updated dengan business requirements

```python
# Performance monitoring example
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"{func.__name__} executed in {duration:.2f}s")
        
        return result
    return wrapper

@monitor_performance
def analyze_division(self, ...):
    # Implementation
    pass
```

## Contoh Lengkap

Berikut adalah contoh lengkap penggunaan sistem:

```python
#!/usr/bin/env python3
"""
Contoh penggunaan Verification Template System
"""

from verification_template_system.core import VerificationEngine, setup_logging
from verification_template_system.config.database_config import DatabaseConfig

def main():
    # 1. Setup logging
    logger = setup_logging(log_level="INFO")
    
    # 2. Load database configuration
    db_config = DatabaseConfig.load_from_config("config.json")
    
    # 3. Initialize verification engine
    engine = VerificationEngine()
    
    # 4. List available templates
    templates = engine.get_available_templates()
    print(f"Available templates: {templates}")
    
    # 5. Run verification
    result = engine.run_verification(
        template_name="transaction_verification",
        estate_name="PGE 2B",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    
    # 6. Process results
    if result['success']:
        print(f"Verification completed successfully!")
        print(f"Total employees processed: {result['summary']['total_employees']}")
        print(f"Verification rate: {result['summary']['verification_rate']:.2f}%")
        
        # Save results
        engine.save_results(result, "verification_results.json")
    else:
        print(f"Verification failed: {result['error']}")
    
    # 7. Cleanup
    engine.cleanup()

if __name__ == "__main__":
    main()
```

Untuk informasi lebih lanjut, silakan lihat dokumentasi API atau hubungi tim development.