#!/usr/bin/env python3
"""
Simple Configuration Service - Hanya untuk Database Path Mapping
Tidak perlu kompleks validation, cukup simple estate name -> database path mapping
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleConfigurationService:
    """
    Simple configuration service - hanya untuk database path mapping
    Tidak ada validation kompleks, langsung read JSON mapping
    """

    def __init__(self, config_file_path: str = None):
        """
        Initialize simple configuration service

        :param config_file_path: Path ke config file (JSON dengan estate -> path mapping)
        """
        if config_file_path is None:
            config_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'database_paths.json'
            )

        self.config_file_path = config_file_path
        self.estate_configs = {}

        logger.info(f"SimpleConfigurationService initialized: {config_file_path}")
        self._load_configurations()

    def _load_configurations(self):
        """Load configurations dari JSON file"""
        try:
            if not os.path.exists(self.config_file_path):
                logger.warning(f"Config file not found: {self.config_file_path}")
                self.estate_configs = {}
                return

            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Validate bahwa ini adalah simple mapping (estate_name -> database_path)
            if isinstance(config_data, dict):
                # Filter hanya string values (abaikan dict atau complex values)
                self.estate_configs = {}
                for estate_name, db_path in config_data.items():
                    if isinstance(db_path, str) and db_path.strip():
                        self.estate_configs[estate_name] = db_path
                    else:
                        logger.warning(f"Skipping invalid config for {estate_name}: {type(db_path)}")

                logger.info(f"Loaded {len(self.estate_configs)} estate configurations")
            else:
                logger.error(f"Invalid config format: expected dict, got {type(config_data)}")
                self.estate_configs = {}

        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            self.estate_configs = {}

    def get_estate_configurations(self) -> Dict[str, str]:
        """
        Get semua estate configurations (estate_name -> database_path)

        :return: Dictionary dengan estate configurations
        """
        return self.estate_configs.copy()

    def get_estate_database_path(self, estate_name: str) -> Optional[str]:
        """
        Get database path untuk estate tertentu

        :param estate_name: Nama estate
        :return: Database path atau None jika tidak ditemukan
        """
        return self.estate_configs.get(estate_name)

    def get_estate_names(self) -> List[str]:
        """
        Get semua nama estate yang tersedia

        :return: List dari estate names
        """
        return list(self.estate_configs.keys())

    def update_estate_path(self, estate_name: str, database_path: str) -> bool:
        """
        Update database path untuk estate

        :param estate_name: Nama estate
        :param database_path: Database path
        :return: True jika berhasil
        """
        try:
            if not estate_name or not estate_name.strip():
                logger.error("Estate name cannot be empty")
                return False

            if not database_path or not database_path.strip():
                logger.error("Database path cannot be empty")
                return False

            self.estate_configs[estate_name] = database_path.strip()
            return self._save_configurations()

        except Exception as e:
            logger.error(f"Error updating estate path: {e}")
            return False

    def add_estate(self, estate_name: str, database_path: str) -> bool:
        """
        Add estate baru

        :param estate_name: Nama estate
        :param database_path: Database path
        :return: True jika berhasil
        """
        return self.update_estate_path(estate_name, database_path)

    def remove_estate(self, estate_name: str) -> bool:
        """
        Remove estate dari configuration

        :param estate_name: Nama estate yang akan dihapus
        :return: True jika berhasil
        """
        try:
            if estate_name in self.estate_configs:
                del self.estate_configs[estate_name]
                return self._save_configurations()
            else:
                logger.warning(f"Estate {estate_name} not found in configuration")
                return False

        except Exception as e:
            logger.error(f"Error removing estate: {e}")
            return False

    def _save_configurations(self) -> bool:
        """Save configurations ke file"""
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_file_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.estate_configs, f, indent=2, ensure_ascii=False)

            logger.info(f"Configurations saved to: {self.config_file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configurations: {e}")
            return False

    def validate_estate_path(self, database_path: str) -> bool:
        """
        Simple validation: check apakah file exists dan .fdb extension

        :param database_path: Database path untuk divalidasi
        :return: True jika valid
        """
        try:
            if not database_path or not database_path.strip():
                return False

            # Check .fdb extension
            if not database_path.lower().endswith('.fdb'):
                return False

            # Check if file exists
            return os.path.exists(database_path.strip())

        except Exception:
            return False

    def get_valid_estates(self) -> Dict[str, str]:
        """
        Get hanya estate dengan valid database paths

        :return: Dictionary dengan valid estate configurations
        """
        valid_estates = {}
        for estate_name, db_path in self.estate_configs.items():
            if self.validate_estate_path(db_path):
                valid_estates[estate_name] = db_path

        logger.info(f"Found {len(valid_estates)} valid estates out of {len(self.estate_configs)} total")
        return valid_estates

    def get_estate_count(self) -> int:
        """Get total jumlah estate"""
        return len(self.estate_configs)

    def get_valid_estate_count(self) -> int:
        """Get jumlah estate dengan valid paths"""
        return len(self.get_valid_estates())

    def reload_configurations(self):
        """Reload configurations dari file"""
        logger.info("Reloading configurations...")
        self._load_configurations()

    def backup_configuration(self) -> str:
        """
        Create backup dari configuration

        :return: Path ke backup file
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.config_file_path}.backup_{timestamp}"

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.estate_configs, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration backed up to: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""

    def get_status(self) -> Dict[str, any]:
        """
        Get configuration status

        :return: Dictionary dengan status information
        """
        valid_estates = self.get_valid_estates()

        return {
            'config_file_path': self.config_file_path,
            'config_file_exists': os.path.exists(self.config_file_path),
            'total_estates': len(self.estate_configs),
            'valid_estates': len(valid_estates),
            'invalid_estates': len(self.estate_configs) - len(valid_estates),
            'estate_names': list(self.estate_configs.keys()),
            'last_loaded': 'Just now'
        }

    def print_status(self):
        """Print configuration status ke console"""
        status = self.get_status()

        print("\n" + "="*50)
        print("SIMPLE CONFIGURATION STATUS")
        print("="*50)
        print(f"Config File: {status['config_file_path']}")
        print(f"File Exists: {status['config_file_exists']}")
        print(f"Total Estates: {status['total_estates']}")
        print(f"Valid Estates: {status['valid_estates']}")
        print(f"Invalid Estates: {status['invalid_estates']}")

        if status['estate_names']:
            print(f"\nEstate Names:")
            for i, name in enumerate(status['estate_names'], 1):
                db_path = self.estate_configs[name]
                valid = self.validate_estate_path(db_path)
                status_icon = "✓" if valid else "✗"
                print(f"  {i}. {name} {status_icon}")

        print("="*50)


# Simple test function
def test_simple_config():
    """Test simple configuration service"""
    print("Testing Simple Configuration Service...")

    # Create instance
    config_service = SimpleConfigurationService()

    # Print status
    config_service.print_status()

    # Test getting configurations
    configs = config_service.get_estate_configurations()
    print(f"\nLoaded {len(configs)} configurations:")

    for estate_name, db_path in list(configs.items())[:3]:  # Show first 3
        valid = config_service.validate_estate_path(db_path)
        print(f"  {estate_name}: {db_path} {'(VALID)' if valid else '(INVALID)'}")


if __name__ == "__main__":
    test_simple_config()