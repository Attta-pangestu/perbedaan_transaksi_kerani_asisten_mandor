"""
Configuration Service - Fixed Version
Manages application configuration and estate settings with improved error handling
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from repositories.configuration_repository import ConfigurationRepository
from models.estate import Estate


class ConfigurationService:
    """
    Service for managing application and estate configurations with improved error handling
    """

    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize configuration service

        :param config_file_path: Optional path to configuration file
        """
        try:
            self.config_repo = ConfigurationRepository(config_file_path)
            self._estates_cache: Dict[str, Estate] = {}
            self._last_cache_update: Optional[datetime] = None
            logger.info("Configuration service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize configuration service: {e}")
            raise

    def load_estate_configurations(self) -> Dict[str, str]:
        """
        Load estate configurations from file

        :return: Dictionary with estate name -> database path mapping
        """
        try:
            config = self.config_repo.load_estate_config()
            logger.info(f"Loaded {len(config)} estate configurations")
            return config
        except Exception as e:
            logger.error(f"Failed to load estate configurations: {e}")
            logger.exception("Full exception details:")
            return {}

    def load_estate_config(self) -> Dict[str, str]:
        """
        Load estate configurations (alias for load_estate_configurations)

        :return: Dictionary with estate name -> database path mapping
        """
        return self.load_estate_configurations()

    def get_estate_config(self, estate_name: str) -> Optional[str]:
        """
        Get specific estate configuration

        :param estate_name: Name of the estate
        :return: Database path for the estate, or None if not found
        """
        try:
            configs = self.load_estate_configurations()
            return configs.get(estate_name)
        except Exception as e:
            logger.error(f"Failed to get estate config for {estate_name}: {e}")
            return None

    def save_estate_configurations(self, config: Dict[str, str]) -> bool:
        """
        Save estate configurations to file

        :param config: Configuration dictionary
        :return: True if successful
        """
        try:
            # Clear cache when configuration changes
            self._estates_cache.clear()
            self._last_cache_update = None

            success = self.config_repo.save_estate_config(config)
            if success:
                logger.info(f"Saved {len(config)} estate configurations")
            return success
        except Exception as e:
            logger.error(f"Failed to save estate configurations: {e}")
            logger.exception("Full exception details:")
            return False

    def get_estate_objects(self, reload: bool = False) -> Dict[str, Estate]:
        """
        Get estate objects from configuration with improved error handling

        :param reload: Force reload from file
        :return: Dictionary with estate name -> Estate object mapping
        """
        try:
            # Check cache
            if (not reload and self._estates_cache and
                self._last_cache_update and
                (datetime.now() - self._last_cache_update).seconds < 300):  # 5 minute cache
                logger.debug("Using cached estate objects")
                return self._estates_cache

            logger.info("Loading estate objects from configuration")

            # Load configuration
            config = self.load_estate_config()
            estates = {}

            for estate_name, db_path in config.items():
                try:
                    # Skip if database path is empty
                    if not db_path or not db_path.strip():
                        logger.warning(f"Skipping estate {estate_name}: empty database path")
                        continue

                    # Create Estate object with validation
                    estate = Estate.from_config(estate_name, db_path)
                    estates[estate_name] = estate

                    logger.debug(f"Created estate object: {estate_name} -> {db_path}")

                except Exception as e:
                    logger.error(f"Failed to create estate object for {estate_name}: {e}")
                    logger.exception("Full exception details:")
                    # Continue with other estates instead of failing completely
                    continue

            # Update cache
            self._estates_cache = estates
            self._last_cache_update = datetime.now()

            logger.info(f"Successfully loaded {len(estates)} estate objects")
            return estates

        except Exception as e:
            logger.error(f"Failed to get estate objects: {e}")
            logger.exception("Full exception details:")
            return {}

    def get_estate_object(self, estate_name: str) -> Optional[Estate]:
        """
        Get specific estate object

        :param estate_name: Name of the estate
        :return: Estate object or None if not found
        """
        try:
            estates = self.get_estate_objects()
            return estates.get(estate_name)
        except Exception as e:
            logger.error(f"Failed to get estate object for {estate_name}: {e}")
            return None

    def validate_estate_configuration(self, estate_name: str, db_path: str) -> Dict[str, Any]:
        """
        Validate a single estate configuration

        :param estate_name: Name of the estate
        :param db_path: Database path
        :return: Validation result
        """
        result = {
            'valid': True,
            'estate_name': estate_name,
            'database_path': db_path,
            'issues': [],
            'warnings': []
        }

        # Validate estate name
        if not estate_name or not estate_name.strip():
            result['valid'] = False
            result['issues'].append("Estate name is empty")

        # Validate database path
        if not db_path or not db_path.strip():
            result['valid'] = False
            result['issues'].append("Database path is empty")
        elif not isinstance(db_path, str):
            result['valid'] = False
            result['issues'].append(f"Database path is not string: {type(db_path)}")
        elif isinstance(db_path, dict):
            result['valid'] = False
            result['issues'].append("Database path is dictionary (likely CSV parsing artifact)")
            if 'tags' in db_path:
                result['issues'].append("Found 'tags' field in database path dictionary")
        elif not os.path.exists(db_path):
            result['warnings'].append("Database file does not exist")

        return result

    def validate_all_estates(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all estate configurations

        :return: Dictionary with validation results for each estate
        """
        logger.info("Validating all estate configurations")

        config = self.load_estate_configurations()
        results = {}

        for estate_name, db_path in config.items():
            try:
                validation_result = self.validate_estate_configuration(estate_name, db_path)
                results[estate_name] = validation_result
            except Exception as e:
                logger.error(f"Error validating estate {estate_name}: {e}")
                results[estate_name] = {
                    'valid': False,
                    'estate_name': estate_name,
                    'database_path': db_path,
                    'issues': [f"Validation error: {e}"],
                    'warnings': []
                }

        logger.info(f"Validated {len(results)} estates")
        valid_count = sum(1 for r in results.values() if r['valid'])
        logger.info(f"Valid estates: {valid_count}/{len(results)}")

        return results

    def get_valid_estates(self) -> Dict[str, Estate]:
        """
        Get only valid estate objects

        :return: Dictionary with valid estate name -> Estate object mapping
        """
        try:
            estates = self.get_estate_objects()
            valid_estates = {}

            for estate_name, estate_obj in estates.items():
                # Validate estate object
                validation_result = self.validate_estate_configuration(
                    estate_obj.name,
                    estate_obj.database_path
                )

                if validation_result['valid']:
                    valid_estates[estate_name] = estate_obj
                else:
                    logger.warning(f"Skipping invalid estate: {estate_name}")
                    if validation_result['issues']:
                        logger.warning(f"  Issues: {', '.join(validation_result['issues'])}")

            logger.info(f"Found {len(valid_estates)} valid estates out of {len(estates)} total")
            return valid_estates

        except Exception as e:
            logger.error(f"Failed to get valid estates: {e}")
            return {}

    def get_estate_configurations_for_analysis(self) -> List[Tuple[str, str]]:
        """
        Get estate configurations suitable for analysis

        :return: List of (estate_name, database_path) tuples
        """
        try:
            valid_estates = self.get_valid_estates()
            configurations = []

            for estate_name, estate_obj in valid_estates.items():
                if estate_obj.database_path and estate_obj.database_path.strip():
                    configurations.append((estate_name, estate_obj.database_path))

            logger.info(f"Returning {len(configurations)} valid configurations for analysis")
            return configurations

        except Exception as e:
            logger.error(f"Failed to get estate configurations for analysis: {e}")
            return []

    def update_estate_path(self, estate_name: str, new_path: str) -> bool:
        """
        Update database path for a specific estate

        :param estate_name: Name of the estate
        :param new_path: New database path
        :return: True if successful
        """
        try:
            # Validate the new path
            validation_result = self.validate_estate_configuration(estate_name, new_path)
            if not validation_result['valid']:
                logger.error(f"Cannot update {estate_name}: validation failed")
                if validation_result['issues']:
                    logger.error(f"  Issues: {', '.join(validation_result['issues'])}")
                return False

            # Load current config
            config = self.load_estate_configurations()

            # Update the path
            config[estate_name] = new_path

            # Save updated config
            success = self.save_estate_configurations(config)

            if success:
                # Clear cache to force reload
                self._estates_cache.clear()
                self._last_cache_update = None
                logger.info(f"Updated database path for {estate_name}: {new_path}")

            return success

        except Exception as e:
            logger.error(f"Failed to update estate path for {estate_name}: {e}")
            logger.exception("Full exception details:")
            return False

    def add_estate(self, estate_name: str, db_path: str) -> bool:
        """
        Add new estate configuration

        :param estate_name: Name of the estate
        :param db_path: Database file path
        :return: True if successful
        """
        try:
            # Validate input
            if not estate_name or not estate_name.strip():
                logger.error("Estate name cannot be empty")
                return False

            if not db_path or not db_path.strip():
                logger.error("Database path cannot be empty")
                return False

            # Load current config
            config = self.load_estate_configurations()

            # Check if estate already exists
            if estate_name in config:
                logger.warning(f"Estate {estate_name} already exists, updating")

            # Add or update estate
            config[estate_name] = db_path

            # Save updated config
            success = self.save_estate_configurations(config)

            if success:
                # Clear cache to force reload
                self._estates_cache.clear()
                self._last_cache_update = None
                logger.info(f"Added/updated estate: {estate_name} -> {db_path}")

            return success

        except Exception as e:
            logger.error(f"Failed to add estate {estate_name}: {e}")
            logger.exception("Full exception details:")
            return False

    def remove_estate(self, estate_name: str) -> bool:
        """
        Remove estate configuration

        :param estate_name: Name of the estate to remove
        :return: True if successful
        """
        try:
            # Load current config
            config = self.load_estate_configurations()

            # Remove estate if exists
            if estate_name not in config:
                logger.warning(f"Estate {estate_name} not found in configuration")
                return False

            del config[estate_name]

            # Save updated config
            success = self.save_estate_configurations(config)

            if success:
                # Clear cache to force reload
                self._estates_cache.clear()
                self._last_cache_update = None
                logger.info(f"Removed estate from configuration: {estate_name}")

            return success

        except Exception as e:
            logger.error(f"Failed to remove estate {estate_name}: {e}")
            logger.exception("Full exception details:")
            return False

    def clear_cache(self):
        """Clear the estates cache"""
        try:
            self._estates_cache.clear()
            self._last_cache_update = None
            logger.info("Cleared estates cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")