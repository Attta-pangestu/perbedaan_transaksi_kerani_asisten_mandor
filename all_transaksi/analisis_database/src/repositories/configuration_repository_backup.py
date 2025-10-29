"""
Configuration Repository
Handles configuration data access and persistence
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class ConfigurationRepository:
    """
    Repository for configuration data management
    """

    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize configuration repository

        :param config_file_path: Path to configuration file
        """
        if config_file_path is None:
            # Default config file path
            config_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'estates_config.json'
            )

        self.config_file_path = config_file_path
        self._ensure_config_directory()

    def _ensure_config_directory(self):
        """Ensure config directory exists"""
        config_dir = os.path.dirname(self.config_file_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

    def get_default_estate_config(self) -> Dict[str, str]:
        """
        Get default estate configuration (empty - no default paths)

        :return: Dictionary with empty estate paths
        """
        return {
            "PGE 1A": "",
            "PGE 1B": "",
            "PGE 2A": "",
            "PGE 2B": "",
            "IJL": "",
            "DME": "",
            "Are B2": "",
            "Are B1": "",
            "Are A": "",
            "Are C": ""
        }

    def load_estate_config(self) -> Dict[str, str]:
        """
        Load estate configuration from file

        :return: Dictionary with estate configurations
        """
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"Loaded configuration from {self.config_file_path}")
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file {self.config_file_path}: {e}")
                print("Using default configuration")
                return self.get_default_estate_config()
        else:
            print(f"Config file {self.config_file_path} not found, creating default")
            default_config = self.get_default_estate_config()
            self.save_estate_config(default_config)
            return default_config

    def save_estate_config(self, config: Dict[str, str]) -> bool:
        """
        Save estate configuration to file

        :param config: Configuration dictionary
        :return: True if successful
        """
        try:
            # Create backup of existing config
            if os.path.exists(self.config_file_path):
                backup_path = f"{self.config_file_path}.backup"
                try:
                    import shutil
                    shutil.copy2(self.config_file_path, backup_path)
                    print(f"Created backup: {backup_path}")
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")

            # Save new config
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            print(f"Configuration saved to {self.config_file_path}")
            return True
        except IOError as e:
            print(f"Error saving config file {self.config_file_path}: {e}")
            return False

    def update_estate_path(self, estate_name: str, new_path: str) -> bool:
        """
        Update path for a specific estate

        :param estate_name: Estate name
        :param new_path: New database path
        :return: True if successful
        """
        config = self.load_estate_config()
        config[estate_name] = new_path
        return self.save_estate_config(config)

    def validate_estate_paths(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all estate paths

        :return: Dictionary with validation results
        """
        config = self.load_estate_config()
        validation_results = {}

        for estate_name, db_path in config.items():
            result = {
                'path': db_path,
                'exists': False,
                'is_file': False,
                'is_directory': False,
                'has_fdb': False,
                'readable': False,
                'validation_message': ''
            }

            try:
                if os.path.exists(db_path):
                    result['exists'] = True
                    result['readable'] = os.access(db_path, os.R_OK)

                    if os.path.isfile(db_path):
                        result['is_file'] = True
                        result['has_fdb'] = db_path.lower().endswith('.fdb')
                        result['validation_message'] = 'Valid database file' if result['has_fdb'] else 'Not a .fdb file'
                    elif os.path.isdir(db_path):
                        result['is_directory'] = True
                        # Check if directory contains .fdb files
                        fdb_files = [f for f in os.listdir(db_path) if f.lower().endswith('.fdb')]
                        if fdb_files:
                            result['has_fdb'] = True
                            result['validation_message'] = f'Directory contains {len(fdb_files)} .fdb file(s)'
                        else:
                            result['validation_message'] = 'Directory contains no .fdb files'
                    else:
                        result['validation_message'] = 'Path exists but is neither file nor directory'
                else:
                    result['validation_message'] = 'Path does not exist'
            except Exception as e:
                result['validation_message'] = f'Error validating path: {e}'

            validation_results[estate_name] = result

        return validation_results

    def get_valid_estate_config(self) -> Dict[str, str]:
        """
        Get configuration with only valid estate paths

        :return: Dictionary with valid estate configurations
        """
        validation_results = self.validate_estate_paths()
        config = self.load_estate_config()

        valid_config = {}
        for estate_name, db_path in config.items():
            validation = validation_results.get(estate_name, {})
            if validation.get('has_fdb', False) and validation.get('readable', False):
                valid_config[estate_name] = db_path

        return valid_config

    def get_estate_connection_settings(self, estate_name: str) -> Dict[str, Any]:
        """
        Get connection settings for a specific estate

        :param estate_name: Estate name
        :return: Dictionary with connection settings
        """
        config = self.load_estate_config()
        db_path = config.get(estate_name)

        if not db_path:
            return {'error': f'Estate {estate_name} not found in configuration'}

        return {
            'estate_name': estate_name,
            'database_path': db_path,
            'username': 'sysdba',
            'password': 'masterkey',
            'use_localhost': False
        }

    def backup_configuration(self, backup_dir: Optional[str] = None) -> str:
        """
        Create backup of configuration file

        :param backup_dir: Optional backup directory
        :return: Path to backup file
        """
        if backup_dir is None:
            backup_dir = os.path.dirname(self.config_file_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"estates_config_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            config = self.load_estate_config()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            print(f"Configuration backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            raise

    def restore_configuration(self, backup_path: str) -> bool:
        """
        Restore configuration from backup

        :param backup_path: Path to backup file
        :return: True if successful
        """
        if not os.path.exists(backup_path):
            print(f"Backup file {backup_path} does not exist")
            return False

        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return self.save_estate_config(config)
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False

    def get_application_settings(self) -> Dict[str, Any]:
        """
        Get application-wide settings

        :return: Dictionary with application settings
        """
        return {
            'default_date_range_days': 31,
            'max_estates_per_analysis': 10,
            'enable_status_704_filter': True,
            'pdf_output_directory': 'reports',
            'auto_backup_config': True,
            'log_level': 'INFO',
            'timeout_seconds': 300,
            'use_localhost_format': False
        }

    def save_application_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save application-wide settings

        :param settings: Settings dictionary
        :return: True if successful
        """
        settings_file = os.path.join(os.path.dirname(self.config_file_path), 'app_settings.json')

        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving application settings: {e}")
            return False

    def load_application_settings(self) -> Dict[str, Any]:
        """
        Load application-wide settings

        :return: Settings dictionary
        """
        settings_file = os.path.join(os.path.dirname(self.config_file_path), 'app_settings.json')

        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading application settings: {e}")

        # Return default settings
        return self.get_application_settings()

    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about configuration

        :return: Dictionary with configuration info
        """
        validation_results = self.validate_estate_paths()

        total_estates = len(validation_results)
        valid_estates = sum(1 for result in validation_results.values()
                           if result.get('has_fdb', False) and result.get('readable', False))

        return {
            'config_file_path': self.config_file_path,
            'config_exists': os.path.exists(self.config_file_path),
            'total_estates': total_estates,
            'valid_estates': valid_estates,
            'invalid_estates': total_estates - valid_estates,
            'validation_rate': (valid_estates / total_estates * 100) if total_estates > 0 else 0,
            'last_modified': datetime.fromtimestamp(
                os.path.getmtime(self.config_file_path)
            ).isoformat() if os.path.exists(self.config_file_path) else None
        }