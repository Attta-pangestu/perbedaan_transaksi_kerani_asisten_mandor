"""
Validation Service
Provides validation services for various data and configurations
"""

import os
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple
from repositories.database_repository import DatabaseRepository
from repositories.configuration_repository import ConfigurationRepository


class ValidationService:
    """
    Service for validating data, configurations, and parameters
    """

    def __init__(self):
        """Initialize validation service"""
        self.config_repo = ConfigurationRepository()

    def validate_date_range(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Validate date range parameters

        :param start_date: Start date
        :param end_date: End date
        :return: Validation result dictionary
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Check if dates are valid
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            result['is_valid'] = False
            result['errors'].append("Invalid date objects provided")
            return result

        # Check if start date is after end date
        if start_date > end_date:
            result['is_valid'] = False
            result['errors'].append("Start date cannot be after end date")
            return result

        # Check if date range is too large (warning)
        days_diff = (end_date - start_date).days + 1
        if days_diff > 365:
            result['warnings'].append(f"Large date range: {days_diff} days. Analysis may take longer.")

        # Check if dates are in the future (warning)
        today = date.today()
        if end_date > today:
            result['warnings'].append("End date is in the future")

        if start_date > today:
            result['warnings'].append("Start date is in the future")

        # Check if dates are too old (warning)
        min_date = date(2020, 1, 1)
        if start_date < min_date:
            result['warnings'].append("Start date is very old. Data may not be available.")

        return result

    def validate_estate_configurations(self, estate_configs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Validate estate configurations

        :param estate_configs: List of (estate_name, db_path) tuples
        :return: Validation result dictionary
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'valid_estates': [],
            'invalid_estates': []
        }

        if not estate_configs:
            result['is_valid'] = False
            result['errors'].append("No estates configured")
            return result

        # Check for duplicate estate names
        estate_names = [config[0] for config in estate_configs]
        if len(estate_names) != len(set(estate_names)):
            result['is_valid'] = False
            result['errors'].append("Duplicate estate names found")
            return result

        # Validate each estate configuration
        for estate_name, db_path in estate_configs:
            estate_validation = self.validate_single_estate(estate_name, db_path)

            if estate_validation['is_valid']:
                result['valid_estates'].append(estate_name)
            else:
                result['invalid_estates'].append(estate_name)
                result['errors'].extend(estate_validation['errors'])

            result['warnings'].extend(estate_validation['warnings'])

        # Check if there are any valid estates
        if not result['valid_estates']:
            result['is_valid'] = False
            result['errors'].append("No valid estate configurations found")

        return result

    def validate_single_estate(self, estate_name: str, db_path: str) -> Dict[str, Any]:
        """
        Validate a single estate configuration

        :param estate_name: Estate name
        :param db_path: Database path
        :return: Validation result dictionary
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Validate estate name
        if not estate_name or not estate_name.strip():
            result['is_valid'] = False
            result['errors'].append("Estate name cannot be empty")

        # Validate database path
        if not db_path or not db_path.strip():
            result['is_valid'] = False
            result['errors'].append(f"Database path cannot be empty for estate {estate_name}")
            return result

        # Check if path exists
        if not os.path.exists(db_path):
            result['is_valid'] = False
            result['errors'].append(f"Database path does not exist: {db_path}")
            return result

        # Check if path is readable
        if not os.access(db_path, os.R_OK):
            result['is_valid'] = False
            result['errors'].append(f"Database path is not readable: {db_path}")
            return result

        # Check path type
        if os.path.isfile(db_path):
            # It's a file, check if it's a .fdb file
            if not db_path.lower().endswith('.fdb'):
                result['warnings'].append(f"Database file does not have .fdb extension: {db_path}")

            # Check file size
            file_size = os.path.getsize(db_path)
            if file_size == 0:
                result['is_valid'] = False
                result['errors'].append(f"Database file is empty: {db_path}")
            elif file_size < 1024:  # Less than 1KB
                result['warnings'].append(f"Database file is very small: {file_size} bytes")

        elif os.path.isdir(db_path):
            # It's a directory, check for .fdb files
            fdb_files = [f for f in os.listdir(db_path) if f.lower().endswith('.fdb')]
            if not fdb_files:
                result['warnings'].append(f"Directory contains no .fdb files: {db_path}")
            else:
                result['warnings'].append(f"Directory contains multiple .fdb files: {len(fdb_files)} files")

        else:
            result['is_valid'] = False
            result['errors'].append(f"Path is neither file nor directory: {db_path}")

        return result

    def validate_database_connection(self, db_path: str, username: str = 'sysdba',
                                   password: str = 'masterkey', use_localhost: bool = False) -> Dict[str, Any]:
        """
        Validate database connection

        :param db_path: Database path
        :param username: Database username
        :param password: Database password
        :param use_localhost: Whether to use localhost format
        :return: Validation result dictionary
        """
        result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'connection_time': None
        }

        start_time = datetime.now()

        try:
            # Create database repository and test connection
            db_repo = DatabaseRepository.create(
                db_path=db_path,
                username=username,
                password=password,
                use_localhost=use_localhost
            )

            if db_repo.test_connection():
                result['is_valid'] = True
            else:
                result['errors'].append("Database connection test failed")

            # Validate database structure
            structure_validation = db_repo.validate_database_structure()
            if not structure_validation['is_valid']:
                result['warnings'].extend(structure_validation['errors'])
                if structure_validation['missing_tables']:
                    result['warnings'].append(f"Missing tables: {structure_validation['missing_tables']}")
                if structure_validation['empty_tables']:
                    result['warnings'].append(f"Empty tables: {structure_validation['empty_tables']}")

        except Exception as e:
            result['errors'].append(f"Connection error: {str(e)}")

        finally:
            end_time = datetime.now()
            result['connection_time'] = (end_time - start_time).total_seconds()

        return result

    def validate_analysis_parameters(self, estate_configs: List[Tuple[str, str]],
                                   start_date: date, end_date: date,
                                   max_estates: int = 10) -> Dict[str, Any]:
        """
        Validate complete analysis parameters

        :param estate_configs: List of estate configurations
        :param start_date: Start date
        :param end_date: End date
        :param max_estates: Maximum number of estates allowed
        :return: Comprehensive validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validation_details': {}
        }

        # Validate date range
        date_validation = self.validate_date_range(start_date, end_date)
        result['validation_details']['date_range'] = date_validation
        if not date_validation['is_valid']:
            result['is_valid'] = False
        result['errors'].extend(date_validation['errors'])
        result['warnings'].extend(date_validation['warnings'])

        # Validate estate configurations
        estate_validation = self.validate_estate_configurations(estate_configs)
        result['validation_details']['estates'] = estate_validation
        if not estate_validation['is_valid']:
            result['is_valid'] = False
        result['errors'].extend(estate_validation['errors'])
        result['warnings'].extend(estate_validation['warnings'])

        # Check estate count limit
        if len(estate_configs) > max_estates:
            result['warnings'].append(f"Number of estates ({len(estate_configs)}) exceeds recommended limit ({max_estates})")

        # Check if there are any valid estates
        if not estate_validation.get('valid_estates'):
            result['is_valid'] = False
            result['errors'].append("No valid estate configurations available")

        return result

    def validate_output_directory(self, output_dir: str) -> Dict[str, Any]:
        """
        Validate output directory for reports

        :param output_dir: Output directory path
        :return: Validation result dictionary
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        if not output_dir:
            output_dir = "reports"  # Default directory

        # Check if directory exists
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                result['warnings'].append(f"Created output directory: {output_dir}")
            except Exception as e:
                result['is_valid'] = False
                result['errors'].append(f"Cannot create output directory {output_dir}: {e}")
                return result

        # Check if directory is writable
        if not os.access(output_dir, os.W_OK):
            result['is_valid'] = False
            result['errors'].append(f"Output directory is not writable: {output_dir}")

        # Check available disk space (warning)
        try:
            stat = os.statvfs(output_dir)
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_space_gb < 1:  # Less than 1GB
                result['warnings'].append(f"Low disk space: {free_space_gb:.2f}GB available")
        except:
            pass  # Disk space check is not critical

        return result

    def validate_transaction_data(self, db_path: str, start_date: date,
                                 end_date: date) -> Dict[str, Any]:
        """
        Validate that transaction data is available for the given date range

        :param db_path: Database path
        :param start_date: Start date
        :param end_date: End date
        :return: Validation result dictionary
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'data_summary': {}
        }

        try:
            db_repo = DatabaseRepository.create(db_path)
            if not db_repo.test_connection():
                result['is_valid'] = False
                result['errors'].append("Cannot connect to database")
                return result

            # Get available date range
            available_range = db_repo.get_available_date_range()
            result['data_summary']['available_range'] = available_range

            # Check if requested range overlaps with available data
            available_start = available_range.get('min_date')
            available_end = available_range.get('max_date')

            if not available_start or not available_end:
                result['is_valid'] = False
                result['errors'].append("No transaction data available in database")
                return result

            # Check for overlap
            if end_date < available_start or start_date > available_end:
                result['is_valid'] = False
                result['errors'].append(
                    f"Requested date range ({start_date} to {end_date}) "
                    f"does not overlap with available data ({available_start} to {available_end})"
                )
            else:
                # Calculate overlap
                overlap_start = max(start_date, available_start)
                overlap_end = min(end_date, available_end)
                overlap_days = (overlap_end - overlap_start).days + 1

                requested_days = (end_date - start_date).days + 1

                if overlap_days < requested_days:
                    result['warnings'].append(
                        f"Partial data coverage: {overlap_days}/{requested_days} days have data"
                    )

                result['data_summary']['overlap_days'] = overlap_days
                result['data_summary']['requested_days'] = requested_days

        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Error validating transaction data: {e}")

        return result

    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """
        Get formatted validation summary

        :param validation_result: Validation result dictionary
        :return: Formatted summary string
        """
        lines = []

        if validation_result['is_valid']:
            lines.append("✓ Validation PASSED")
        else:
            lines.append("✗ Validation FAILED")

        if validation_result.get('errors'):
            lines.append("\nERRORS:")
            for error in validation_result['errors']:
                lines.append(f"  • {error}")

        if validation_result.get('warnings'):
            lines.append("\nWARNINGS:")
            for warning in validation_result['warnings']:
                lines.append(f"  • {warning}")

        # Add details if available
        details = validation_result.get('validation_details', {})
        if details:
            lines.append("\nVALIDATION DETAILS:")
            for key, value in details.items():
                if isinstance(value, dict) and value.get('is_valid') is not None:
                    status = "✓" if value['is_valid'] else "✗"
                    lines.append(f"  {key}: {status}")
                    if value.get('errors'):
                        for error in value['errors']:
                            lines.append(f"    - {error}")

        return "\n".join(lines)