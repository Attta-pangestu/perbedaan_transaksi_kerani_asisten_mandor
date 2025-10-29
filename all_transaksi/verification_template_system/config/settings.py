"""
System Settings
Pengaturan sistem untuk verification template system.
"""

import os
from pathlib import Path
from typing import Dict, Any


class Settings:
    """
    Pengaturan sistem untuk verification template system.
    """
    
    # Direktori sistem
    BASE_DIR = Path(__file__).parent.parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = BASE_DIR / "reports"
    
    # Pengaturan logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Pengaturan database
    DB_CONNECTION_TIMEOUT = 30  # seconds
    DB_QUERY_TIMEOUT = 300      # seconds
    
    # Pengaturan verifikasi
    DEFAULT_BATCH_SIZE = 1000
    MAX_RETRY_ATTEMPTS = 3
    
    # Filter khusus untuk bulan tertentu (dari logika asli)
    SPECIAL_MONTH_FILTER = {
        "month": 5,  # Mei
        "status_filter": "704",
        "description": "Filter TRANSSTATUS 704 untuk bulan Mei"
    }
    
    # Field yang dibandingkan dalam verifikasi transaksi
    COMPARISON_FIELDS = [
        'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 
        'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT'
    ]
    
    # Record tags untuk analisis
    RECORD_TAGS = {
        'KERANI': 'PM',
        'MANDOR': 'P1', 
        'ASISTEN': 'P5'
    }
    
    @classmethod
    def ensure_directories(cls):
        """
        Pastikan semua direktori yang diperlukan ada.
        """
        directories = [cls.LOGS_DIR, cls.REPORTS_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_template_path(cls, template_name: str) -> Path:
        """
        Dapatkan path lengkap untuk template.
        
        Args:
            template_name: Nama template (tanpa ekstensi .json)
        
        Returns:
            Path: Path lengkap ke file template
        """
        return cls.TEMPLATES_DIR / f"{template_name}.json"
    
    @classmethod
    def get_log_path(cls, log_name: str) -> Path:
        """
        Dapatkan path lengkap untuk file log.
        
        Args:
            log_name: Nama file log (tanpa ekstensi .log)
        
        Returns:
            Path: Path lengkap ke file log
        """
        return cls.LOGS_DIR / f"{log_name}.log"
    
    @classmethod
    def get_report_path(cls, report_name: str) -> Path:
        """
        Dapatkan path lengkap untuk file report.
        
        Args:
            report_name: Nama file report
        
        Returns:
            Path: Path lengkap ke file report
        """
        return cls.REPORTS_DIR / report_name
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        Convert settings ke dictionary.
        
        Returns:
            Dict: Settings dalam format dictionary
        """
        return {
            'base_dir': str(cls.BASE_DIR),
            'templates_dir': str(cls.TEMPLATES_DIR),
            'logs_dir': str(cls.LOGS_DIR),
            'reports_dir': str(cls.REPORTS_DIR),
            'log_level': cls.LOG_LEVEL,
            'db_connection_timeout': cls.DB_CONNECTION_TIMEOUT,
            'db_query_timeout': cls.DB_QUERY_TIMEOUT,
            'default_batch_size': cls.DEFAULT_BATCH_SIZE,
            'max_retry_attempts': cls.MAX_RETRY_ATTEMPTS,
            'special_month_filter': cls.SPECIAL_MONTH_FILTER,
            'comparison_fields': cls.COMPARISON_FIELDS,
            'record_tags': cls.RECORD_TAGS
        }


# Environment-specific settings
class DevelopmentSettings(Settings):
    """Settings untuk development environment."""
    LOG_LEVEL = "DEBUG"
    DB_CONNECTION_TIMEOUT = 10


class ProductionSettings(Settings):
    """Settings untuk production environment."""
    LOG_LEVEL = "WARNING"
    DB_CONNECTION_TIMEOUT = 60


def get_settings() -> Settings:
    """
    Dapatkan settings berdasarkan environment.
    
    Returns:
        Settings: Instance settings yang sesuai
    """
    env = os.getenv('VERIFICATION_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionSettings()
    else:
        return DevelopmentSettings()


if __name__ == "__main__":
    # Test settings
    print("=== System Settings ===")
    
    settings = get_settings()
    settings.ensure_directories()
    
    print(f"Environment: {os.getenv('VERIFICATION_ENV', 'development')}")
    print(f"Base directory: {settings.BASE_DIR}")
    print(f"Templates directory: {settings.TEMPLATES_DIR}")
    print(f"Logs directory: {settings.LOGS_DIR}")
    print(f"Reports directory: {settings.REPORTS_DIR}")
    
    print("\nSettings dictionary:")
    for key, value in settings.to_dict().items():
        print(f"  {key}: {value}")
    
    print(f"\nTemplate path example: {settings.get_template_path('transaction_verification')}")
    print(f"Log path example: {settings.get_log_path('verification_2025_01')}")
    print(f"Report path example: {settings.get_report_path('verification_report.pdf')}")