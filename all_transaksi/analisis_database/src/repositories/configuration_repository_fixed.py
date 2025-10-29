"""
Configuration Repository - Fixed Version
Handles configuration data access and persistence with better error handling
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationRepositoryFixed:
    """
    Repository for configuration data management with improved error handling
    """

    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize configuration repository

        :param config_file_path: Path to configuration file
        """
        if config_file_path is None:
            # Use database_paths.json instead of estates_config.json
            config_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'database_paths.json'
            )

        self.config_file_path = config_file_path
        logger.info(f"Configuration repository initialized with path: {self.config_file_path}")
        self._ensure_config_directory()

    def _ensure_config_directory(self):
        """Ensure config directory exists"""
        config_dir = os.path.dirname(self.config_file_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"Created config directory: {config_dir}")

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
        Load estate configuration from file with improved error handling

        :return: Dictionary with estate configurations
        """
        logger.info(f"Loading estate configuration from: {self.config_file_path}")

        if not os.path.exists(self.config_file_path):
            logger.warning(f"Config file not found: {self.config_file_path}")
            logger.info("Creating default configuration file")
            default_config = self.get_default_estate_config()
            self.save_estate_config(default_config)
            return default_config

        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Validate configuration structure
            if not isinstance(config, dict):
                logger.error(f"Invalid configuration format: expected dict, got {type(config)}")
                return self.get_default_estate_config()

            # Validate each estate entry
            validated_config = {}
            for estate_name, db_path in config.items():
                # Ensure estate_name is string
                if not isinstance(estate_name, str):
                    logger.warning(f"Invalid estate name type: {type(estate_name)}, skipping: {estate_name}")
                    continue

                # Validate db_path
                if db_path is None:
                    logger.warning(f"Database path is None for estate: {estate_name}")
                    db_path = ""
                elif not isinstance(db_path, str):
                    logger.warning(f"Invalid database path type: {type(db_path)} for estate: {estate_name}")
                    # Try to convert to string
                    try:
                        db_path = str(db_path)
                    except Exception as e:
                        logger.error(f"Cannot convert database path to string for {estate_name}: {e}")
                        db_path = ""

                # Check for potential CSV/Excel parsing artifacts
                if isinstance(db_path, dict):
                    logger.error(f"Database path is dict instead of string for estate: {estate_name}")
                    logger.error(f"Dict keys: {list(db_path.keys())}")
                    if 'tags' in db_path:
                        logger.error(f"Found 'tags' field in dict! This is likely a CSV parsing artifact")
                    # Convert dict to string representation
                    db_path = str(db_path.get('database_path', db_path.get('path', str(db_path))))

                validated_config[estate_name] = db_path

            logger.info(f"Successfully loaded configuration with {len(validated_config)} estates")
            return validated_config

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in config file {self.config_file_path}: {e}")
            logger.error("This might be caused by:")
            logger.error("  - Invalid JSON syntax")
            logger.error("  - File corruption")
            logger.error("  - Encoding issues")
            logger.info("Using default configuration")
            return self.get_default_estate_config()

        except IOError as e:
            logger.error(f"IO error reading config file {self.config_file_path}: {e}")
            logger.info("Using default configuration")
            return self.get_default_estate_config()

        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            logger.error("Full traceback:")
            logger.exception("Full exception details:")
            return self.get_default_estate_config()

    def save_estate_config(self, config: Dict[str, str]) -> bool:
        """
        Save estate configuration to file with validation

        :param config: Configuration dictionary
        :return: True if successful
        """
        try:
            # Validate config before saving
            validated_config = {}
            for estate_name, db_path in config.items():
                if not isinstance(estate_name, str):
                    logger.error(f"Invalid estate name: {estate_name}, skipping")
                    continue

                if not isinstance(db_path, str):
                    logger.warning(f"Converting database path to string for {estate_name}")
                    db_path = str(db_path)

                validated_config[estate_name] = db_path

            # Create backup before saving
            if os.path.exists(self.config_file_path):
                backup_path = f"{self.config_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    import shutil
                    shutil.copy2(self.config_file_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to create backup: {e}")

            # Save configuration
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully saved configuration to {self.config_file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            logger.exception("Full exception details:")
            return False

    def validate_configuration(self, config: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate configuration and return validation results

        :param config: Configuration dictionary
        :return: Dictionary with validation results
        """
        results = {
            'valid': True,
            'estates': [],
            'issues': [],
            'warnings': []
        }

        for estate_name, db_path in config.items():
            estate_result = {
                'name': estate_name,
                'path': db_path,
                'valid': True,
                'issues': [],
                'warnings': []
            }

            # Validate estate name
            if not estate_name or not estate_name.strip():
                estate_result['valid'] = False
                estate_result['issues'].append("Empty estate name")
                results['valid'] = False

            # Validate database path
            if not db_path:
                estate_result['valid'] = False
                estate_result['issues'].append("Empty database path")
                results['valid'] = False
            elif not isinstance(db_path, str):
                estate_result['valid'] = False
                estate_result['issues'].append(f"Invalid database path type: {type(db_path)}")
                results['valid'] = False
            elif isinstance(db_path, dict):
                estate_result['valid'] = False
                estate_result['issues'].append("Database path is dict (CSV parsing artifact)")
                results['valid'] = False
                if 'tags' in db_path:
                    estate_result['issues'].append("Found 'tags' field in dict")
            elif not os.path.exists(db_path):
                estate_result['warnings'].append("Database file does not exist")

            results['estates'].append(estate_result)

            if estate_result['issues']:
                results['issues'].extend([f"{estate_name}: {issue}" for issue in estate_result['issues']])
            if estate_result['warnings']:
                results['warnings'].extend([f"{estate_name}: {warning}" for warning in estate_result['warnings']])

        return results

    def get_estate_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about estate configurations

        :return: Dictionary with statistics
        """
        config = self.load_estate_config()
        validation_results = self.validate_configuration(config)

        stats = {
            'total_estates': len(config),
            'valid_estates': len([e for e in validation_results['estates'] if e['valid']]),
            'estates_with_paths': len([e for e in validation_results['estates'] if e['path'] and e['path'].strip()]),
            'estates_with_existing_files': len([e for e in validation_results['estates'] if e['path'] and os.path.exists(e['path'])]),
            'total_issues': len(validation_results['issues']),
            'total_warnings': len(validation_results['warnings']),
            'validation_passed': validation_results['valid']
        }

        return stats