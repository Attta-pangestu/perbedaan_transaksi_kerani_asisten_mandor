"""
Test suite for automated report system
Tests GUI functionality, data validation, and report generation
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from business.services.automated_report_service import AutomatedReportService
from presentation.widgets.automated_report_widget import AutomatedReportWidget
from datetime import datetime


class TestAutomatedReportService(unittest.TestCase):
    """Test cases for AutomatedReportService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = AutomatedReportService()
        
        # Sample test data
        self.sample_data = [
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN001',
                'amount': 1000
            },
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN002',
                'amount': 1500
            },
            {
                'tanggal': '2024-01-16',
                'unit': '8',
                'estate': '2A',
                'transno': 'TXN003',
                'amount': 2000
            }
        ]
    
    def test_validate_report_data_valid(self):
        """Test data validation with valid data"""
        result = self.service.validate_report_data(self.sample_data, unit='9', estate='2B')
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertGreaterEqual(result['data_quality_score'], 70)
    
    def test_validate_report_data_empty(self):
        """Test data validation with empty data"""
        result = self.service.validate_report_data([], unit='9', estate='2B')
        
        self.assertFalse(result['is_valid'])
        self.assertIn("Tidak ada data untuk divalidasi", result['errors'])
        self.assertEqual(result['data_quality_score'], 0)
    
    def test_validate_report_data_missing_fields(self):
        """Test data validation with missing required fields"""
        invalid_data = [
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                # Missing 'estate' and 'transno'
                'amount': 1000
            }
        ]
        
        result = self.service.validate_report_data(invalid_data, unit='9', estate='2B')
        
        self.assertGreater(len(result['warnings']), 0)
        self.assertLess(result['data_quality_score'], 100)
    
    def test_validate_report_data_invalid_date_format(self):
        """Test data validation with invalid date format"""
        invalid_data = [
            {
                'tanggal': 'invalid-date',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN001',
                'amount': 1000
            }
        ]
        
        result = self.service.validate_report_data(invalid_data, unit='9', estate='2B')
        
        self.assertGreater(len(result['warnings']), 0)
        self.assertLess(result['data_quality_score'], 100)
    
    def test_validate_report_data_duplicates(self):
        """Test data validation with duplicate transno"""
        duplicate_data = [
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN001',
                'amount': 1000
            },
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN001',  # Duplicate
                'amount': 1500
            }
        ]
        
        result = self.service.validate_report_data(duplicate_data, unit='9', estate='2B')
        
        self.assertGreater(len(result['warnings']), 0)
        self.assertLess(result['data_quality_score'], 100)
    
    def test_validate_report_data_unit_estate_filter(self):
        """Test data validation with unit and estate filtering"""
        result = self.service.validate_report_data(self.sample_data, unit='9', estate='2B')
        
        # Should find data for Unit 9 Estate 2B
        self.assertTrue(result['is_valid'])
        
        # Test with non-existent unit/estate
        result_empty = self.service.validate_report_data(self.sample_data, unit='99', estate='99')
        
        self.assertGreater(len(result_empty['warnings']), 0)
        self.assertLess(result_empty['data_quality_score'], 100)
    
    @patch('pandas.DataFrame')
    @patch('openpyxl.Workbook')
    @patch('os.makedirs')
    def test_format_excel_output(self, mock_makedirs, mock_workbook, mock_dataframe):
        """Test Excel output formatting"""
        mock_wb = Mock()
        mock_ws = Mock()
        mock_wb.active = mock_ws
        mock_workbook.return_value = mock_wb
        
        mock_df = Mock()
        mock_df.columns = ['tanggal', 'unit', 'estate', 'transno']
        mock_df.values = [['2024-01-15', '9', '2B', 'TXN001']]
        mock_dataframe.return_value = mock_df
        
        result = self.service._format_excel_output(self.sample_data, 'Unit9_Estate2B', '20240115_120000')
        
        self.assertIsInstance(result, str)
        self.assertIn('Laporan_Unit9_Estate2B_20240115_120000.xlsx', result)
        mock_wb.save.assert_called_once()
    
    @patch('pandas.DataFrame')
    @patch('os.makedirs')
    def test_format_csv_output(self, mock_makedirs, mock_dataframe):
        """Test CSV output formatting"""
        mock_df = Mock()
        mock_dataframe.return_value = mock_df
        
        result = self.service._format_csv_output(self.sample_data, 'Unit9_Estate2B', '20240115_120000')
        
        self.assertIsInstance(result, str)
        self.assertIn('Laporan_Unit9_Estate2B_20240115_120000.csv', result)
        mock_df.to_csv.assert_called_once()
    
    def test_format_report_output_invalid_format(self):
        """Test format_report_output with invalid format"""
        with self.assertRaises(ValueError):
            self.service.format_report_output(self.sample_data, format_type='invalid_format')


class TestAutomatedReportWidget(unittest.TestCase):
    """Test cases for AutomatedReportWidget GUI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        
        # Mock the service
        self.mock_service = Mock(spec=AutomatedReportService)
        
        # Create widget with mocked service
        with patch('presentation.widgets.automated_report_widget.AutomatedReportService', return_value=self.mock_service):
            self.widget = AutomatedReportWidget(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        self.root.destroy()
    
    def test_widget_initialization(self):
        """Test widget initialization"""
        self.assertIsNotNone(self.widget.main_frame)
        self.assertIsNotNone(self.widget.config_tree)
        self.assertIsNotNone(self.widget.control_buttons)
    
    def test_load_configurations(self):
        """Test loading configurations"""
        # Mock service response
        mock_configs = [
            {
                'name': 'Test Config',
                'unit': '9',
                'estate': '2B',
                'frequency': 'Harian',
                'time': '08:00',
                'enabled': True,
                'last_run': '2024-01-15T08:00:00'
            }
        ]
        self.mock_service.get_all_configurations.return_value = mock_configs
        
        # Load configurations
        self.widget.load_configurations()
        
        # Verify service was called
        self.mock_service.get_all_configurations.assert_called_once()
        
        # Check if data was added to tree
        children = self.widget.config_tree.get_children()
        self.assertEqual(len(children), 1)
    
    def test_add_default_configurations(self):
        """Test adding default configurations"""
        # Mock service response
        self.mock_service.save_configuration.return_value = 'config_id_123'
        
        # Mock messagebox
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            self.widget.add_default_configurations()
            
            # Verify service was called
            self.mock_service.save_configuration.assert_called_once()
            
            # Verify success message was shown
            mock_showinfo.assert_called_once()
    
    def test_add_default_configurations_error(self):
        """Test adding default configurations with error"""
        # Mock service to return None (error)
        self.mock_service.save_configuration.return_value = None
        
        # Mock messagebox
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            self.widget.add_default_configurations()
            
            # Verify error message was shown
            mock_showerror.assert_called_once()
    
    def test_widget_buttons_exist(self):
        """Test that all required buttons exist"""
        required_buttons = ['add', 'edit', 'delete', 'run_now', 'refresh', 'add_default']
        
        for button_key in required_buttons:
            self.assertIn(button_key, self.widget.control_buttons)
            self.assertIsNotNone(self.widget.control_buttons[button_key])


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for real-world usage"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.service = AutomatedReportService()
    
    def test_unit_9_estate_2b_scenario(self):
        """Test complete scenario for Unit 9 Estate 2B"""
        # Sample data for Unit 9 Estate 2B
        test_data = [
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN001',
                'amount': 1000,
                'description': 'Test transaction 1'
            },
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN002',
                'amount': 1500,
                'description': 'Test transaction 2'
            }
        ]
        
        # Step 1: Validate data
        validation_result = self.service.validate_report_data(test_data, unit='9', estate='2B')
        
        self.assertTrue(validation_result['is_valid'])
        self.assertGreaterEqual(validation_result['data_quality_score'], 70)
        
        # Step 2: Test different output formats
        formats_to_test = ['csv']  # Only test CSV to avoid external dependencies
        
        for format_type in formats_to_test:
            try:
                output_path = self.service.format_report_output(
                    test_data, 
                    format_type=format_type, 
                    unit='9', 
                    estate='2B'
                )
                
                self.assertIsInstance(output_path, str)
                self.assertIn('Unit9_Estate2B', output_path)
                
                # Clean up generated file
                if os.path.exists(output_path):
                    os.remove(output_path)
                    
            except Exception as e:
                self.fail(f"Failed to generate {format_type} report: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with minimal data
        minimal_data = [
            {
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': 'TXN001'
            }
        ]
        
        validation_result = self.service.validate_report_data(minimal_data, unit='9', estate='2B')
        self.assertIsInstance(validation_result, dict)
        self.assertIn('is_valid', validation_result)
        
        # Test with large dataset (simulate)
        large_data = []
        for i in range(1000):
            large_data.append({
                'tanggal': '2024-01-15',
                'unit': '9',
                'estate': '2B',
                'transno': f'TXN{i:04d}',
                'amount': i * 100
            })
        
        validation_result = self.service.validate_report_data(large_data, unit='9', estate='2B')
        self.assertTrue(validation_result['is_valid'])
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with None data
        result = self.service.validate_report_data(None, unit='9', estate='2B')
        self.assertFalse(result['is_valid'])
        
        # Test with invalid data structure
        invalid_data = "not a list"
        result = self.service.validate_report_data(invalid_data, unit='9', estate='2B')
        self.assertFalse(result['is_valid'])


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAutomatedReportService))
    test_suite.addTest(unittest.makeSuite(TestAutomatedReportWidget))
    test_suite.addTest(unittest.makeSuite(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")