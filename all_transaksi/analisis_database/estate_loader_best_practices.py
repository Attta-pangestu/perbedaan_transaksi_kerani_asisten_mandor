#!/usr/bin/env python3
"""
Best Practices untuk Estate Loading - Pencegahan Error "Invalid column index tags"
Schema validation, configuration fleksibel, dan error prevention
"""

import json
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging
from dataclasses import dataclass, field
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileFormat(Enum):
    """Supported file formats"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    AUTO = "auto"


@dataclass
class EstateSchema:
    """Schema definition untuk estate data"""
    required_columns: List[str] = field(default_factory=lambda: ['id', 'name'])
    optional_columns: List[str] = field(default_factory=lambda: ['description', 'tags', 'database_path'])
    column_types: Dict[str, type] = field(default_factory=lambda: {
        'id': str,
        'name': str,
        'description': str,
        'tags': str,
        'database_path': str
    })

    def get_all_columns(self) -> List[str]:
        """Get all required and optional columns"""
        return self.required_columns + self.optional_columns

    def validate_column_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate column types and return validation results"""
        validation_results = {
            'valid': True,
            'type_mismatches': [],
            'missing_columns': [],
            'extra_columns': []
        }

        # Check required columns
        for col in self.required_columns:
            if col not in df.columns:
                validation_results['missing_columns'].append(col)
                validation_results['valid'] = False

        # Check column types
        for col in df.columns:
            if col in self.column_types:
                expected_type = self.column_types[col]
                actual_type = df[col].dtype

                # Handle pandas type conversion
                if expected_type == str and actual_type != 'object':
                    validation_results['type_mismatches'].append({
                        'column': col,
                        'expected': 'string',
                        'actual': str(actual_type)
                    })

        return validation_results


class EstateConfigurationManager:
    """
    Manager untuk konfigurasi estate yang fleksibel dan robust
    """

    def __init__(self, config_path: str = None, schema: EstateSchema = None):
        """
        Initialize configuration manager

        :param config_path: Path ke file konfigurasi
        :param schema: Schema definition untuk validasi
        """
        self.config_path = Path(config_path) if config_path else None
        self.schema = schema or EstateSchema()
        self.config_data = {}
        self.validation_results = {}

        logger.info(f"EstateConfigurationManager initialized")

    def load_configuration(self, format_type: FileFormat = FileFormat.AUTO) -> bool:
        """
        Load konfigurasi dengan robust error handling

        :param format_type: Format file (AUTO untuk deteksi otomatis)
        :return: True jika berhasil
        """
        if not self.config_path or not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            return False

        try:
            # Load file dengan format detection
            if format_type == FileFormat.AUTO:
                format_type = self._detect_file_format()

            logger.info(f"Loading configuration in {format_type.value} format")

            if format_type == FileFormat.JSON:
                self.config_data = self._load_json_config()
            elif format_type == FileFormat.CSV:
                self.config_data = self._load_csv_config()
            elif format_type == FileFormat.EXCEL:
                self.config_data = self._load_excel_config()

            # Validate configuration
            self._validate_configuration()

            # Fix common issues
            self._fix_configuration_issues()

            logger.info(f"Configuration loaded successfully: {len(self.config_data)} estates")
            return True

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.exception("Full traceback:")
            return False

    def _detect_file_format(self) -> FileFormat:
        """Detect file format dari extension"""
        if not self.config_path:
            return FileFormat.CSV

        ext = self.config_path.suffix.lower()
        if ext == '.json':
            return FileFormat.JSON
        elif ext in ['.xlsx', '.xls']:
            return FileFormat.EXCEL
        else:
            return FileFormat.CSV

    def _load_json_config(self) -> Dict[str, Any]:
        """Load JSON configuration dengan robust handling"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, dict):
            # Check if it's a flat estate configuration
            if all(not isinstance(v, dict) for v in data.values()):
                # Simple key-value configuration (estate_name -> database_path)
                return self._convert_simple_config_to_estate_data(data)
            else:
                # Complex configuration
                return data
        elif isinstance(data, list):
            return {'estates': data}
        else:
            raise ValueError(f"Unsupported JSON structure: {type(data)}")

    def _convert_simple_config_to_estate_data(self, simple_config: Dict[str, str]) -> Dict[str, Any]:
        """Convert simple config (estate_name -> db_path) ke full estate data"""
        estates = []
        for estate_name, db_path in simple_config.items():
            if isinstance(db_path, str):  # Only include string values
                estates.append({
                    'id': estate_name.replace(' ', '_').lower(),
                    'name': estate_name,
                    'description': f'Estate {estate_name}',
                    'tags': 'estate,production',
                    'database_path': db_path
                })

        return {'estates': estates}

    def _load_csv_config(self) -> Dict[str, Any]:
        """Load CSV configuration"""
        df = pd.read_csv(self.config_path)
        return {'estates': df.to_dict('records')}

    def _load_excel_config(self) -> Dict[str, Any]:
        """Load Excel configuration"""
        df = pd.read_excel(self.config_path)
        return {'estates': df.to_dict('records')}

    def _validate_configuration(self):
        """Validate configuration structure"""
        if 'estates' not in self.config_data:
            raise ValueError("Invalid configuration: missing 'estates' key")

        estates = self.config_data['estates']
        if not isinstance(estates, list):
            raise ValueError("Invalid configuration: 'estates' must be a list")

        # Validate each estate
        validated_estates = []
        validation_errors = []

        for i, estate in enumerate(estates):
            try:
                validated_estate = self._validate_single_estate(estate, i)
                validated_estates.append(validated_estate)
            except Exception as e:
                validation_errors.append(f"Estate {i}: {e}")

        self.validation_results = {
            'total_estates': len(estates),
            'valid_estates': len(validated_estates),
            'validation_errors': validation_errors,
            'valid': len(validation_errors) == 0
        }

        if not self.validation_results['valid']:
            logger.warning(f"Configuration validation failed: {len(validation_errors)} errors")

        # Update config with validated estates
        self.config_data['estates'] = validated_estates

    def _validate_single_estate(self, estate: Dict, index: int) -> Dict[str, Any]:
        """Validate single estate data"""
        validated_estate = {}

        # Check required fields
        for field in self.schema.required_columns:
            if field not in estate:
                raise ValueError(f"Missing required field: {field}")

            value = estate[field]
            if not value or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Empty required field: {field}")

            # Fix dict values (parsing artifacts)
            if isinstance(value, dict):
                logger.warning(f"Fixed dict value in {field} for estate {index}")
                value = self._extract_value_from_dict(value, field)

            validated_estate[field] = value

        # Handle optional fields
        for field in self.schema.optional_columns:
            value = estate.get(field, '')

            # Fix dict values
            if isinstance(value, dict):
                logger.warning(f"Fixed dict value in {field} for estate {index}")
                value = self._extract_value_from_dict(value, field)

            # Set default values for missing fields
            if not value and field == 'description':
                validated_estate[field] = f"Estate {validated_estate.get('name', 'Unknown')}"
            elif not value and field == 'tags':
                validated_estate[field] = 'estate,production'
            else:
                validated_estate[field] = value

        return validated_estate

    def _extract_value_from_dict(self, dict_value: Dict, field_name: str) -> str:
        """Extract meaningful value dari dict (parsing artifact)"""
        # Try common keys based on field type
        if field_name == 'tags':
            for key in ['tags', 'value', 'name']:
                if key in dict_value:
                    val = dict_value[key]
                    if isinstance(val, list):
                        return ','.join(str(v) for v in val)
                    return str(val)
        elif field_name == 'database_path':
            for key in ['database_path', 'path', 'value', 'location']:
                if key in dict_value:
                    return str(dict_value[key])
        else:
            for key in ['value', 'name', field_name]:
                if key in dict_value:
                    return str(dict_value[key])

        # Fallback: convert to string
        return str(dict_value)

    def _fix_configuration_issues(self):
        """Fix common configuration issues"""
        if not self.validation_results.get('valid', True):
            logger.info("Attempting to fix configuration issues...")

            # Additional fixes can be added here
            # For example: duplicate detection, path validation, etc.

    def get_estate_configurations(self) -> Dict[str, str]:
        """
        Get estate configurations dalam format sederhana (name -> database_path)

        :return: Dictionary dengan estate configurations
        """
        if not self.config_data or 'estates' not in self.config_data:
            return {}

        configurations = {}
        for estate in self.config_data['estates']:
            name = estate.get('name', '')
            db_path = estate.get('database_path', '')

            if name and db_path and isinstance(db_path, str):
                configurations[name] = db_path

        return configurations

    def save_configuration(self, output_path: str, format_type: FileFormat = FileFormat.JSON) -> bool:
        """
        Save configuration ke file

        :param output_path: Path output file
        :param format_type: Format output
        :return: True jika berhasil
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format_type == FileFormat.JSON:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            elif format_type == FileFormat.CSV:
                df = pd.DataFrame(self.config_data['estates'])
                df.to_csv(output_path, index=False)
            elif format_type == FileFormat.EXCEL:
                df = pd.DataFrame(self.config_data['estates'])
                df.to_excel(output_path, index=False)

            logger.info(f"Configuration saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def get_validation_report(self) -> str:
        """Get detailed validation report"""
        if not self.validation_results:
            return "No validation performed"

        report = []
        report.append("VALIDATION REPORT")
        report.append("=" * 30)
        report.append(f"Total Estates: {self.validation_results['total_estates']}")
        report.append(f"Valid Estates: {self.validation_results['valid_estates']}")
        report.append(f"Validation Status: {'✅ PASSED' if self.validation_results['valid'] else '❌ FAILED'}")

        if self.validation_results['validation_errors']:
            report.append("\nValidation Errors:")
            for error in self.validation_results['validation_errors']:
                report.append(f"  ❌ {error}")

        return '\n'.join(report)

    @staticmethod
    def create_backup_config(original_path: str, backup_suffix: str = "_backup") -> str:
        """
        Create backup dari configuration file

        :param original_path: Path file asli
        :param backup_suffix: Suffix untuk backup file
        :return: Path backup file
        """
        original_path = Path(original_path)
        backup_path = original_path.parent / f"{original_path.stem}{backup_suffix}{original_path.suffix}"

        if original_path.exists():
            import shutil
            shutil.copy2(original_path, backup_path)
            logger.info(f"Configuration backed up to: {backup_path}")

        return str(backup_path)


# Usage example dan testing
if __name__ == "__main__":
    print("Testing Estate Configuration Manager")
    print("=" * 40)

    # Test dengan existing configuration
    config_path = "config/database_paths.json"

    try:
        manager = EstateConfigurationManager(config_path)

        # Load configuration
        success = manager.load_configuration()
        print(f"Configuration loaded: {success}")

        if success:
            # Get validation report
            print("\n" + manager.get_validation_report())

            # Get simple configurations
            configs = manager.get_estate_configurations()
            print(f"\nLoaded {len(configs)} estate configurations:")
            for name, path in list(configs.items())[:3]:  # Show first 3
                print(f"  {name}: {path}")

            # Test saving in different formats
            manager.save_configuration("config/backup_estates.json", FileFormat.JSON)
            manager.save_configuration("config/backup_estates.csv", FileFormat.CSV)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()