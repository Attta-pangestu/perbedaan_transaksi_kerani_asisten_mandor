"""
Integration Tests untuk FFB Analysis System

Test file untuk memvalidasi integrasi antar modul dan end-to-end functionality
"""

import unittest
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock imports for GUI dependencies
sys.modules['tkinter'] = Mock()
sys.modules['tkinter.ttk'] = Mock()
sys.modules['tkinter.messagebox'] = Mock()
sys.modules['tkinter.filedialog'] = Mock()
sys.modules['tkcalendar'] = Mock()

try:
    from core.config import FFBConfig
    from core.business_logic import FFBVerificationEngine, FFBDataProcessor
    from database.firebird_connector import FirebirdConnector
    from database.query_builder import FFBQueryBuilder
    from analysis.verification_engine import FFBVerificationEngine as AnalysisEngine
except ImportError as e:
    print(f"Warning: Could not import modules for integration testing: {e}")


class TestSystemIntegration(unittest.TestCase):
    """
    Test cases untuk system integration
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.test_dir = tempfile.mkdtemp()
        self.config = FFBConfig(config_dir=self.test_dir)

    def tearDown(self):
        """
        Cleanup test environment
        """
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_config_initialization(self):
        """
        Test configuration system initialization
        """
        # Test default configuration creation
        self.assertIsNotNone(self.config.estate_config)
        self.assertIsNotNone(self.config.report_config)
        self.assertIsNotNone(self.config.analysis_config)

        # Test estate operations
        estates = self.config.get_all_estates()
        self.assertGreater(len(estates), 0)

        # Test path validation
        paths = self.config.validate_estate_paths()
        self.assertIsInstance(paths, dict)
        self.assertEqual(len(paths), len(estates))

    def test_query_builder_and_config_integration(self):
        """
        Test integration between query builder and configuration
        """
        query_builder = FFBQueryBuilder()

        # Test table name generation with config
        months = self.config.get_month_list_from_range("2025-09-01", "2025-10-31")
        self.assertEqual(set(months), {9, 10})

        for month in months:
            table_name = query_builder.get_monthly_table_name(month)
            expected_name = self.config.get_table_name_for_month(month)
            self.assertEqual(table_name, expected_name)

    def test_data_processor_and_verification_integration(self):
        """
        Test integration between data processor and verification engine
        """
        # Create sample raw data
        raw_data = pd.DataFrame({
            'TRANSNO': ['T001', 'T001', 'T002', 'T003'],
            'SCANUSERID': ['U001', 'U002', 'U001', 'U003'],
            'RECORDTAG': ['PM', 'P1', 'PM', 'PM'],
            'TRANSDATE': ['2025-09-01', '2025-09-01', '2025-09-02', '2025-09-03'],
            'FIELDID': ['F001', 'F001', 'F002', 'F003'],
            'AFD': ['A1', 'A1', 'A2', 'A3'],
            'BLOCK': ['B1', 'B1', 'B2', 'B3'],
            'TREECOUNT': [100, 100, 150, 200],
            'BUNCHCOUNT': [50, 50, 75, 100],
            'DIVNAME': ['PGE 1A', 'PGE 1A', 'PGE 1B', 'PGE 1C']
        })

        # Process data
        processor = FFBDataProcessor()
        processed_data = processor.preprocess_data(raw_data)

        # Verify transactions
        verification_engine = FFBVerificationEngine()
        results = verification_engine.verify_transactions(processed_data)

        # Check integration results
        self.assertIn('verification_rate', results)
        self.assertGreaterEqual(results['verification_rate'], 0)

        # Test performance analysis
        performance_results = verification_engine.analyze_employee_performance(
            processed_data, results
        )

        if performance_results:
            self.assertIn('performance_data', performance_results)

    def test_end_to_end_analysis_simulation(self):
        """
        Test end-to-end analysis workflow simulation
        """
        # Simulate multi-estate data
        estates_data = {
            'PGE 1A': self._create_estate_sample_data('PGE 1A'),
            'PGE 1B': self._create_estate_sample_data('PGE 1B')
        }

        # Initialize components
        processor = FFBDataProcessor()
        verification_engine = FFBVerificationEngine()
        query_builder = FFBQueryBuilder()

        analysis_results = {
            'estates': {},
            'summary': {}
        }

        # Process each estate
        for estate_name, raw_data in estates_data.items():
            # Preprocess data
            processed_data = processor.preprocess_data(raw_data)

            # Filter by date range
            filtered_data = processor.filter_by_date_range(
                processed_data, '2025-09-01', '2025-09-30'
            )

            # Verify transactions
            verification_results = verification_engine.verify_transactions(filtered_data)

            # Analyze performance
            performance_results = verification_engine.analyze_employee_performance(
                filtered_data, verification_results
            )

            # Store results
            analysis_results['estates'][estate_name] = {
                'verification': verification_results,
                'performance': performance_results,
                'data_summary': {
                    'total_records': len(filtered_data),
                    'unique_transno': filtered_data['TRANSNO'].nunique() if 'TRANSNO' in filtered_data.columns else 0
                }
            }

        # Generate cross-estate summary
        total_records = sum(
            estate_data['data_summary']['total_records']
            for estate_data in analysis_results['estates'].values()
        )

        analysis_results['summary'] = {
            'total_estates': len(estates_data),
            'total_records': total_records,
            'analysis_timestamp': datetime.now().isoformat()
        }

        # Validate results
        self.assertEqual(len(analysis_results['estates']), 2)
        self.assertIn('PGE 1A', analysis_results['estates'])
        self.assertIn('PGE 1B', analysis_results['estates'])
        self.assertGreater(analysis_results['summary']['total_records'], 0)

    def _create_estate_sample_data(self, estate_name: str) -> pd.DataFrame:
        """
        Create sample data for a specific estate
        """
        import random
        random.seed(42)  # For reproducible results

        data = []
        for i in range(50):
            transno = f"T{estate_name.replace(' ', '')}{i+1:03d}"
            has_verification = random.random() > 0.3  # 70% verification rate

            # PM record
            data.append({
                'TRANSNO': transno,
                'SCANUSERID': f"U{random.randint(1, 5):03d}",
                'RECORDTAG': 'PM',
                'TRANSDATE': f"2025-09-{random.randint(1, 30):02d}",
                'FIELDID': f"F{random.randint(1, 10):03d}",
                'AFD': f"A{random.randint(1, 5)}",
                'BLOCK': f"B{random.randint(1, 20):02d}",
                'TREECOUNT': random.randint(50, 300),
                'BUNCHCOUNT': random.randint(25, 150),
                'DIVNAME': estate_name
            })

            # Add verification record
            if has_verification:
                data.append({
                    'TRANSNO': transno,
                    'SCANUSERID': f"V{random.randint(1, 3):03d}",
                    'RECORDTAG': random.choice(['P1', 'P5']),
                    'TRANSDATE': f"2025-09-{random.randint(1, 30):02d}",
                    'FIELDID': f"F{random.randint(1, 10):03d}",
                    'AFD': f"A{random.randint(1, 5)}",
                    'BLOCK': f"B{random.randint(1, 20):02d}",
                    'TREECOUNT': random.randint(50, 300),
                    'BUNCHCOUNT': random.randint(25, 150),
                    'DIVNAME': estate_name
                })

        return pd.DataFrame(data)


class TestConfigurationIntegration(unittest.TestCase):
    """
    Test configuration management integration
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        Cleanup test environment
        """
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_configuration_persistence(self):
        """
        Test configuration persistence and loading
        """
        # Initialize config with custom directory
        config1 = FFBConfig(config_dir=self.test_dir)

        # Modify configuration
        config1.update_estate_path('TEST_ESTATE', 'new_path/test.fdb')

        # Create new config instance (should load modified data)
        config2 = FFBConfig(config_dir=self.test_dir)

        # Verify persistence
        self.assertEqual(config2.get_estate_path('TEST_ESTATE'), 'new_path/test.fdb')

    def test_configuration_validation(self):
        """
        Test configuration validation
        """
        config = FFBConfig(config_dir=self.test_dir)

        # Test estate path validation
        paths = config.validate_estate_paths()
        self.assertIsInstance(paths, dict)

        # All configured estates should be in validation results
        estates = config.get_all_estates()
        for estate in estates:
            self.assertIn(estate, paths)

    def test_month_and_date_integration(self):
        """
        Test month calculation and date range integration
        """
        config = FFBConfig(config_dir=self.test_dir)

        # Test various date ranges
        test_cases = [
            ('2025-09-01', '2025-09-30', [9]),
            ('2025-09-15', '2025-10-15', [9, 10]),
            ('2025-01-01', '2025-12-31', list(range(1, 13))),
            ('2025-12-01', '2025-12-31', [12])
        ]

        for start_date, end_date, expected_months in test_cases:
            months = config.get_month_list_from_range(start_date, end_date)
            self.assertEqual(set(months), set(expected_months))

            # Test table name generation
            for month in months:
                table_name = config.get_table_name_for_month(month)
                expected_name = f"FFBSCANNERDATA{month:02d}"
                self.assertEqual(table_name, expected_name)


class TestErrorHandling(unittest.TestCase):
    """
    Test error handling and edge cases
    """

    def test_empty_data_handling(self):
        """
        Test handling of empty data
        """
        # Empty DataFrame
        empty_df = pd.DataFrame()

        verification_engine = FFBVerificationEngine()
        results = verification_engine.verify_transactions(empty_df)

        # Should handle empty data gracefully
        self.assertEqual(results['total_transactions'], 0)
        self.assertEqual(results['verification_rate'], 0)

        # Test data processor with empty data
        processor = FFBDataProcessor()
        processed = processor.preprocess_data(empty_df)
        self.assertTrue(processed.empty)

    def test_invalid_date_handling(self):
        """
        Test handling of invalid dates
        """
        processor = FFBDataProcessor()

        data_with_invalid_dates = pd.DataFrame({
            'TRANSNO': ['T001', 'T002'],
            'TRANSDATE': ['invalid-date', '2025-09-01'],
            'SCANUSERID': ['U001', 'U002'],
            'RECORDTAG': ['PM', 'PM']
        })

        processed = processor.preprocess_data(data_with_invalid_dates)

        # Should handle invalid dates gracefully
        self.assertLessEqual(len(processed), len(data_with_invalid_dates))

    def test_missing_columns_handling(self):
        """
        Test handling of missing columns
        """
        # Data with missing essential columns
        incomplete_data = pd.DataFrame({
            'TRANSNO': ['T001', 'T002'],
            'SCANUSERID': ['U001', 'U002']
            # Missing RECORDTAG and other essential columns
        })

        processor = FFBDataProcessor()
        processed = processor.preprocess_data(incomplete_data)

        # Should handle missing columns
        # Either return empty data or data with default values
        self.assertIsInstance(processed, pd.DataFrame)

    def test_config_file_errors(self):
        """
        Test handling of configuration file errors
        """
        # Test with non-existent config directory
        test_dir = tempfile.mkdtemp()
        shutil.rmtree(test_dir)  # Remove directory immediately

        try:
            config = FFBConfig(config_dir=test_dir)
            # Should create default configuration
            self.assertIsNotNone(config.estate_config)
        except Exception as e:
            self.fail(f"Config initialization should not fail: {e}")


if __name__ == '__main__':
    # Configure test environment
    print("FFB Analysis System - Integration Tests")
    print("=" * 50)

    # Run tests
    unittest.main(verbosity=2)