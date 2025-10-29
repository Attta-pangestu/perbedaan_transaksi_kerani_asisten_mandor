#!/usr/bin/env python3
"""
Robust Estate Loader - Solusi Komprehensif untuk "Invalid column index tags" Error
Handles CSV/Excel parsing with dynamic column validation and error recovery
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobustEstateLoader:
    """
    Loader untuk data estate dengan validasi dinamis dan error handling
    """

    def __init__(self, file_path: str, expected_columns: List[str] = None):
        """
        Initialize estate loader

        :param file_path: Path ke file (CSV/Excel/JSON)
        :param expected_columns: Daftar kolom yang diharapkan
        """
        self.file_path = Path(file_path)
        self.expected_columns = expected_columns or ['id', 'name', 'description', 'tags', 'database_path']
        self.data = None
        self.validation_results = {}

        logger.info(f"RobustEstateLoader initialized for: {file_path}")

    def load_estate(self, estate_name: str = None) -> Dict[str, Any]:
        """
        Load estate data dengan robust error handling

        :param estate_name: Nama estate spesifik (optional)
        :return: Dictionary dengan estate data
        """
        try:
            logger.info(f"Loading estate data from: {self.file_path}")

            # Step 1: Load file dengan format detection
            self.data = self._load_file_with_format_detection()

            # Step 2: Validate structure
            self._validate_data_structure()

            # Step 3: Fix common issues
            self._fix_common_parsing_issues()

            # Step 4: Extract estate data
            if estate_name:
                return self._extract_specific_estate(estate_name)
            else:
                return self._extract_all_estates()

        except Exception as e:
            logger.error(f"Error loading estate data: {e}")
            logger.exception("Full traceback:")
            return self._create_fallback_response(estate_name, str(e))

    def _load_file_with_format_detection(self) -> pd.DataFrame:
        """Load file dengan automatic format detection"""
        try:
            # Detect file format
            if self.file_path.suffix.lower() == '.csv':
                logger.info("Loading CSV file")
                return pd.read_csv(self.file_path)
            elif self.file_path.suffix.lower() in ['.xlsx', '.xls']:
                logger.info("Loading Excel file")
                return pd.read_excel(self.file_path)
            elif self.file_path.suffix.lower() == '.json':
                logger.info("Loading JSON file")
                return self._load_json_as_dataframe()
            else:
                # Try CSV as fallback
                logger.warning(f"Unknown file format {self.file_path.suffix}, trying CSV")
                return pd.read_csv(self.file_path)

        except Exception as e:
            logger.error(f"Failed to load file {self.file_path}: {e}")
            raise

    def _load_json_as_dataframe(self) -> pd.DataFrame:
        """Load JSON file dan convert ke DataFrame dengan robust handling"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, dict):
                # Convert dict to DataFrame
                if 'estates' in data:
                    # Nested structure
                    return pd.DataFrame(data['estates'])
                else:
                    # Flat structure
                    return pd.DataFrame([data])
            elif isinstance(data, list):
                # List of dictionaries
                return pd.DataFrame(data)
            else:
                raise ValueError(f"Unsupported JSON structure: {type(data)}")

        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            raise

    def _validate_data_structure(self):
        """Validate data structure dan detect issues"""
        if self.data is None or self.data.empty:
            raise ValueError("No data loaded or empty dataset")

        logger.info(f"Data shape: {self.data.shape}")
        logger.info(f"Columns: {list(self.data.columns)}")

        # Check for expected columns
        missing_columns = [col for col in self.expected_columns if col not in self.data.columns]
        if missing_columns:
            logger.warning(f"Missing expected columns: {missing_columns}")
            self.validation_results['missing_columns'] = missing_columns

        # Check for dict-type columns (parsing artifacts)
        dict_columns = []
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                sample_values = self.data[col].dropna().head(5)
                if any(isinstance(val, dict) for val in sample_values):
                    dict_columns.append(col)

        if dict_columns:
            logger.warning(f"Found dict-type columns (parsing artifacts): {dict_columns}")
            self.validation_results['dict_columns'] = dict_columns

    def _fix_common_parsing_issues(self):
        """Fix common parsing issues"""
        # Fix dict-type columns
        if 'dict_columns' in self.validation_results:
            for col in self.validation_results['dict_columns']:
                self._fix_dict_column(col)

        # Fix missing columns
        if 'missing_columns' in self.validation_results:
            for col in self.validation_results['missing_columns']:
                self._add_missing_column(col)

    def _fix_dict_column(self, column_name: str):
        """Fix column yang mengandung dict values"""
        logger.info(f"Fixing dict column: {column_name}")

        def extract_value_from_dict(val):
            if isinstance(val, dict):
                # Try common keys
                for key in ['value', 'name', 'path', 'database_path', 'tags']:
                    if key in val:
                        return val[key]
                # Convert to string as fallback
                return str(val)
            return val

        self.data[column_name] = self.data[column_name].apply(extract_value_from_dict)

    def _add_missing_column(self, column_name: str):
        """Add missing column dengan default values"""
        logger.info(f"Adding missing column: {column_name}")

        if column_name == 'tags':
            self.data[column_name] = ''  # Empty string for tags
        elif column_name == 'description':
            self.data[column_name] = 'No description'  # Default description
        else:
            self.data[column_name] = None  # Null for other columns

    def _extract_specific_estate(self, estate_name: str) -> Dict[str, Any]:
        """Extract data untuk estate spesifik"""
        if 'name' in self.data.columns:
            estate_data = self.data[self.data['name'] == estate_name]
        elif 'id' in self.data.columns:
            estate_data = self.data[self.data['id'] == estate_name]
        else:
            # Try to find in any column
            estate_data = self.data[self.data.apply(lambda row: estate_name in str(row.values), axis=1)]

        if estate_data.empty:
            logger.warning(f"Estate '{estate_name}' not found in data")
            return self._create_fallback_response(estate_name, "Estate not found")

        return self._format_estate_response(estate_data.iloc[0].to_dict())

    def _extract_all_estates(self) -> Dict[str, Any]:
        """Extract semua estate data"""
        estates = {}

        for _, row in self.data.iterrows():
            estate_name = row.get('name', row.get('id', f"estate_{len(estates)}"))
            estates[estate_name] = self._format_estate_response(row.to_dict())

        return {
            'success': True,
            'estates': estates,
            'total_count': len(estates),
            'validation_results': self.validation_results
        }

    def _format_estate_response(self, estate_data: Dict) -> Dict[str, Any]:
        """Format estate data response"""
        # Extract tags dengan robust handling
        tags = estate_data.get('tags', '')
        if isinstance(tags, str):
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        elif isinstance(tags, list):
            tags_list = tags
        elif isinstance(tags, dict):
            # Handle dict tags
            tags_list = [str(v) for v in tags.values() if v]
        else:
            tags_list = []

        return {
            'id': estate_data.get('id', ''),
            'name': estate_data.get('name', ''),
            'description': estate_data.get('description', ''),
            'database_path': estate_data.get('database_path', estate_data.get('path', '')),
            'tags': tags_list,
            'raw_data': estate_data
        }

    def _create_fallback_response(self, estate_name: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback response untuk error cases"""
        return {
            'success': False,
            'error': error_msg,
            'estate_name': estate_name,
            'fallback_data': {
                'id': estate_name or '',
                'name': estate_name or '',
                'description': 'Error loading data',
                'database_path': '',
                'tags': []
            },
            'debug_info': {
                'file_path': str(self.file_path),
                'expected_columns': self.expected_columns,
                'actual_columns': list(self.data.columns) if self.data is not None else [],
                'validation_results': self.validation_results
            }
        }

    def debug_print_structure(self):
        """Print debugging information about file structure"""
        print("=" * 60)
        print("DEBUGGING ESTATE LOADER")
        print("=" * 60)

        try:
            print(f"File Path: {self.file_path}")
            print(f"File Exists: {self.file_path.exists()}")
            print(f"File Size: {self.file_path.stat().st_size} bytes")

            if self.data is not None:
                print(f"\nData Shape: {self.data.shape}")
                print(f"Columns: {list(self.data.columns)}")
                print(f"Data Types:\n{self.data.dtypes}")

                print(f"\nFirst 5 Rows:")
                print(self.data.head())

                print(f"\nSample Values per Column:")
                for col in self.data.columns:
                    sample_vals = self.data[col].dropna().head(3).tolist()
                    print(f"  {col}: {sample_vals}")
            else:
                print("No data loaded")

        except Exception as e:
            print(f"Error during debugging: {e}")
            traceback.print_exc()

    @staticmethod
    def create_test_cases():
        """Create test cases untuk validation"""
        return {
            'valid_csv': {
                'description': 'Valid CSV with all required columns',
                'data': {
                    'columns': ['id', 'name', 'description', 'tags', 'database_path'],
                    'sample_row': ['1', 'PGE 1A', 'Estate description', 'palm_oil,production', '/path/to/db.fdb']
                }
            },
            'missing_tags_column': {
                'description': 'CSV missing tags column',
                'data': {
                    'columns': ['id', 'name', 'description', 'database_path'],
                    'sample_row': ['1', 'PGE 1A', 'Estate description', '/path/to/db.fdb']
                }
            },
            'dict_parsing_artifact': {
                'description': 'CSV with dict-type values (parsing artifact)',
                'data': {
                    'columns': ['id', 'name', 'tags'],
                    'sample_row': ['1', 'PGE 1A', "{'tags': ['palm_oil', 'production']}"]
                }
            },
            'empty_file': {
                'description': 'Empty file',
                'data': {'columns': [], 'sample_row': []}
            }
        }


# Example usage dan testing
if __name__ == "__main__":
    # Test dengan file configuration
    config_path = "config/database_paths.json"

    print("Testing Robust Estate Loader")
    print("=" * 40)

    try:
        loader = RobustEstateLoader(config_path)

        # Debug structure
        loader.debug_print_structure()

        # Load all estates
        result = loader.load_estate()
        print(f"\nLoading Result:")
        print(json.dumps(result, indent=2, default=str))

        # Test specific estate
        if result.get('success') and result.get('estates'):
            first_estate = list(result['estates'].keys())[0]
            specific_result = loader.load_estate(first_estate)
            print(f"\nSpecific Estate Result ({first_estate}):")
            print(json.dumps(specific_result, indent=2, default=str))

    except Exception as e:
        print(f"Error in testing: {e}")
        traceback.print_exc()

    # Print test cases
    print("\n" + "=" * 60)
    print("TEST CASES FOR VALIDATION")
    print("=" * 60)

    test_cases = RobustEstateLoader.create_test_cases()
    for case_name, case_info in test_cases.items():
        print(f"\nTest Case: {case_name}")
        print(f"Description: {case_info['description']}")
        print(f"Expected Behavior: {case_info['data']}")