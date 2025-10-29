"""
Database Configuration Template
Template konfigurasi database yang dapat disesuaikan untuk berbagai estate/database.
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path


class DatabaseConfig:
    """
    Template konfigurasi database Firebird.
    Dapat dikustomisasi untuk berbagai estate dan jenis verifikasi.
    """
    
    def __init__(self, db_path: str, estate_name: str = "Default Estate"):
        """
        Inisialisasi konfigurasi database.
        
        Args:
            db_path: Path ke file database Firebird (.fdb)
            estate_name: Nama estate untuk identifikasi
        """
        self.db_path = db_path
        self.estate_name = estate_name
        self.connection_params = {
            'dsn': db_path,
            'user': 'SYSDBA',
            'password': 'masterkey',
            'charset': 'UTF8'
        }
    
    @classmethod
    def load_from_template(cls, config_file: Optional[str] = None) -> 'DatabaseConfig':
        """
        Load konfigurasi dari file template JSON.
        
        Args:
            config_file: Path ke file konfigurasi JSON. Jika None, akan mencari config.json
                        di direktori parent atau menggunakan default.
        
        Returns:
            DatabaseConfig: Instance konfigurasi database
        """
        if config_file is None:
            # Cari config.json di direktori parent (sesuai struktur proyek)
            current_dir = Path(__file__).parent.parent
            config_file = current_dir.parent / "config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Ambil database pertama dari config (sesuai permintaan user)
                if config_data:
                    estate_name, db_path = next(iter(config_data.items()))
                    return cls(db_path, estate_name)
                else:
                    raise ValueError("Config file kosong")
                    
            except (json.JSONDecodeError, IOError) as e:
                raise ValueError(f"Gagal memuat config file {config_file}: {e}")
        else:
            # Gunakan konfigurasi default jika file tidak ditemukan
            return cls._get_default_config()
    
    @classmethod
    def _get_default_config(cls) -> 'DatabaseConfig':
        """
        Konfigurasi default jika tidak ada file config.
        
        Returns:
            DatabaseConfig: Konfigurasi default
        """
        default_path = r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB"
        return cls(default_path, "PGE 2B (Default)")
    
    @classmethod
    def create_template_config(cls, estate_configs: Dict[str, str], output_file: str):
        """
        Membuat file template konfigurasi untuk multiple estate.
        
        Args:
            estate_configs: Dictionary {estate_name: db_path}
            output_file: Path output file JSON
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(estate_configs, f, indent=4, ensure_ascii=False)
            print(f"Template konfigurasi berhasil dibuat: {output_file}")
        except IOError as e:
            raise ValueError(f"Gagal membuat template config: {e}")
    
    def validate_database_path(self) -> bool:
        """
        Validasi apakah path database valid.
        
        Returns:
            bool: True jika path valid dan file exists
        """
        # Handle path yang berupa direktori (seperti PGE 2A di config asli)
        if os.path.isdir(self.db_path):
            # Cari file .FDB di dalam direktori
            for file in os.listdir(self.db_path):
                if file.upper().endswith('.FDB'):
                    self.db_path = os.path.join(self.db_path, file)
                    return True
            return False
        
        return os.path.exists(self.db_path) and self.db_path.upper().endswith('.FDB')
    
    def get_connection_string(self) -> str:
        """
        Generate connection string untuk Firebird.
        
        Returns:
            str: Connection string
        """
        return self.db_path
    
    def to_dict(self) -> Dict:
        """
        Convert konfigurasi ke dictionary.
        
        Returns:
            Dict: Konfigurasi dalam format dictionary
        """
        return {
            'estate_name': self.estate_name,
            'db_path': self.db_path,
            'connection_params': self.connection_params,
            'is_valid': self.validate_database_path()
        }
    
    def __str__(self) -> str:
        """String representation of the config."""
        return f"DatabaseConfig(estate='{self.estate_name}', db_path='{self.db_path}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"DatabaseConfig(estate_name='{self.estate_name}', db_path='{self.db_path}', valid={self.validate_database_path()})"


# Template konfigurasi untuk berbagai jenis verifikasi
VERIFICATION_TEMPLATES = {
    "transaction_verification": {
        "description": "Template verifikasi transaksi FFB Scanner",
        "required_tables": ["FFBSCANNERDATA01", "FFBSCANNERDATA02", "FFBSCANNERDATA03", 
                           "FFBSCANNERDATA04", "FFBSCANNERDATA05", "FFBSCANNERDATA06",
                           "FFBSCANNERDATA07", "FFBSCANNERDATA08", "FFBSCANNERDATA09",
                           "FFBSCANNERDATA10", "FFBSCANNERDATA11", "FFBSCANNERDATA12",
                           "OCFIELD", "EMP", "CRDIVISION"],
        "date_range_required": True,
        "division_filter_required": True
    },
    "employee_performance": {
        "description": "Template verifikasi performa karyawan",
        "required_tables": ["EMP", "FFBSCANNERDATA01", "FFBSCANNERDATA02", "FFBSCANNERDATA03",
                           "FFBSCANNERDATA04", "FFBSCANNERDATA05", "FFBSCANNERDATA06",
                           "FFBSCANNERDATA07", "FFBSCANNERDATA08", "FFBSCANNERDATA09",
                           "FFBSCANNERDATA10", "FFBSCANNERDATA11", "FFBSCANNERDATA12"],
        "date_range_required": True,
        "division_filter_required": False
    }
}


if __name__ == "__main__":
    # Contoh penggunaan
    print("=== Database Configuration Template ===")
    
    # Load dari config.json
    try:
        config = DatabaseConfig.load_from_template()
        print(f"Loaded config: {config}")
        print(f"Config details: {config.to_dict()}")
    except Exception as e:
        print(f"Error loading config: {e}")
    
    # Contoh membuat template config baru
    sample_configs = {
        "PGE 1A": r"C:\Database\PTRJ_P1A.FDB",
        "PGE 1B": r"C:\Database\PTRJ_P1B.FDB",
        "PGE 2A": r"C:\Database\PTRJ_P2A.FDB"
    }
    
    try:
        DatabaseConfig.create_template_config(sample_configs, "sample_config.json")
    except Exception as e:
        print(f"Error creating template: {e}")