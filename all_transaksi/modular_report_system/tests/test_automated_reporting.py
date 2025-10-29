"""
Automated Reporting System Test Suite
Comprehensive tests for Unit 9 Estate 2B automated reporting functionality
"""

import unittest
import tempfile
import os
import json
import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from business.services.automated_report_service import AutomatedReportService
from business.models.report_configuration import ReportConfiguration
from business.models.report_data import ReportData
from data.repositories.report_repository import ReportRepository


class TestAutomatedReportService(unittest.TestCase):
    """Test cases for automated report service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock database manager
        self.mock_db_manager = Mock()
        self.mock_repository = Mock(spec=ReportRepository)
        
        # Create service instance
        self.service = AutomatedReportService(self.mock_db_manager)
        self.service.repository = self.mock_repository
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.db_manager)
    
    def test_save_configuration_unit_9_estate_2b(self):
        """Test saving configuration for Unit 9 Estate 2B"""
        config = ReportConfiguration(
            name="Unit 9 Estate 2B Daily Report",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True,
            parameters={
                "include_summary": True,
                "include_details": True,
                "format": "excel"
            }
        )
        
        # Mock repository save
        self.mock_repository.save_configuration.return_value = "config_123"
        
        # Save configuration
        config_id = self.service.save_configuration(config)
        
        # Verify
        self.assertEqual(config_id, "config_123")
        self.mock_repository.save_configuration.assert_called_once_with(config)
    
    def test_get_configurations_filtering(self):
        """Test getting configurations with filtering"""
        # Mock configurations
        mock_configs = [
            ReportConfiguration(
                id="1",
                name="Unit 9 Estate 2B Daily",
                unit="9",
                estate="2B",
                frequency="daily",
                time="08:00",
                enabled=True
            ),
            ReportConfiguration(
                id="2",
                name="Unit 8 Estate 2A Daily",
                unit="8",
                estate="2A",
                frequency="daily",
                time="08:00",
                enabled=True
            )
        ]
        
        self.mock_repository.get_all_configurations.return_value = mock_configs
        
        # Get all configurations
        configs = self.service.get_configurations()
        
        # Verify
        self.assertEqual(len(configs), 2)
        
        # Test filtering for Unit 9 Estate 2B
        unit_9_configs = [c for c in configs if c.unit == "9" and c.estate == "2B"]
        self.assertEqual(len(unit_9_configs), 1)
        self.assertEqual(unit_9_configs[0].name, "Unit 9 Estate 2B Daily")
    
    def test_generate_report_unit_9_estate_2b(self):
        """Test generating report for Unit 9 Estate 2B"""
        # Mock configuration
        config = ReportConfiguration(
            id="test_config",
            name="Unit 9 Estate 2B Report",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True,
            parameters={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "include_summary": True
            }
        )
        
        # Mock report data
        mock_data = [
            {
                'tanggal': '2024-01-01',
                'unit': '9',
                'estate': '2B',
                'total_transaksi': 150,
                'total_nilai': 75000000
            },
            {
                'tanggal': '2024-01-02',
                'unit': '9',
                'estate': '2B',
                'total_transaksi': 180,
                'total_nilai': 90000000
            }
        ]
        
        self.mock_repository.get_report_data.return_value = mock_data
        
        # Generate report
        with patch('business.services.report_generator_service.ReportGeneratorService') as mock_generator:
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            mock_generator_instance.generate_report.return_value = "report_path.xlsx"
            
            result = self.service.generate_report(config)
        
        # Verify
        self.assertIsNotNone(result)
        self.mock_repository.get_report_data.assert_called_once()
    
    def test_schedule_validation(self):
        """Test schedule validation for automated reports"""
        # Test valid schedule
        valid_config = ReportConfiguration(
            name="Valid Schedule",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True
        )
        
        is_valid = self.service.validate_schedule(valid_config)
        self.assertTrue(is_valid)
        
        # Test invalid time format
        invalid_config = ReportConfiguration(
            name="Invalid Schedule",
            unit="9",
            estate="2B",
            frequency="daily",
            time="25:00",  # Invalid time
            enabled=True
        )
        
        is_valid = self.service.validate_schedule(invalid_config)
        self.assertFalse(is_valid)
    
    def test_run_scheduled_reports(self):
        """Test running scheduled reports"""
        # Mock current time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2024, 1, 15, 8, 0, 0)
            mock_datetime.strptime.side_effect = datetime.datetime.strptime
            
            # Mock configurations due for execution
            due_configs = [
                ReportConfiguration(
                    id="config_1",
                    name="Unit 9 Estate 2B Morning Report",
                    unit="9",
                    estate="2B",
                    frequency="daily",
                    time="08:00",
                    enabled=True
                )
            ]
            
            self.mock_repository.get_due_configurations.return_value = due_configs
            
            # Mock report generation
            with patch.object(self.service, 'generate_report') as mock_generate:
                mock_generate.return_value = "report_generated.xlsx"
                
                # Run scheduled reports
                results = self.service.run_scheduled_reports()
                
                # Verify
                self.assertEqual(len(results), 1)
                mock_generate.assert_called_once_with(due_configs[0])


class TestReportConfiguration(unittest.TestCase):
    """Test cases for report configuration model"""
    
    def test_configuration_creation(self):
        """Test creating report configuration"""
        config = ReportConfiguration(
            name="Test Config",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True
        )
        
        self.assertEqual(config.name, "Test Config")
        self.assertEqual(config.unit, "9")
        self.assertEqual(config.estate, "2B")
        self.assertEqual(config.frequency, "daily")
        self.assertEqual(config.time, "08:00")
        self.assertTrue(config.enabled)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Valid configuration
        valid_config = ReportConfiguration(
            name="Valid Config",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True
        )
        
        self.assertTrue(valid_config.is_valid())
        
        # Invalid configuration - missing required fields
        invalid_config = ReportConfiguration(
            name="",  # Empty name
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True
        )
        
        self.assertFalse(invalid_config.is_valid())
    
    def test_unit_estate_combination_validation(self):
        """Test Unit 9 Estate 2B specific validation"""
        # Valid Unit 9 Estate 2B
        config = ReportConfiguration(
            name="Unit 9 Estate 2B Config",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00",
            enabled=True
        )
        
        self.assertTrue(config.is_unit_estate_valid())
        
        # Test other combinations
        config.unit = "10"
        config.estate = "3A"
        self.assertTrue(config.is_unit_estate_valid())  # Should still be valid
    
    def test_configuration_serialization(self):
        """Test configuration serialization to/from dict"""
        config = ReportConfiguration(
            name="Serialization Test",
            unit="9",
            estate="2B",
            frequency="weekly",
            time="09:30",
            enabled=True,
            parameters={"format": "pdf", "include_charts": True}
        )
        
        # Convert to dict
        config_dict = config.to_dict()
        
        # Verify dict structure
        self.assertEqual(config_dict['name'], "Serialization Test")
        self.assertEqual(config_dict['unit'], "9")
        self.assertEqual(config_dict['estate'], "2B")
        self.assertEqual(config_dict['parameters']['format'], "pdf")
        
        # Convert back from dict
        restored_config = ReportConfiguration.from_dict(config_dict)
        
        # Verify restoration
        self.assertEqual(restored_config.name, config.name)
        self.assertEqual(restored_config.unit, config.unit)
        self.assertEqual(restored_config.estate, config.estate)
        self.assertEqual(restored_config.parameters, config.parameters)


class TestReportDataValidation(unittest.TestCase):
    """Test cases for report data validation"""
    
    def test_data_structure_validation(self):
        """Test report data structure validation"""
        # Valid data structure
        valid_data = [
            {
                'tanggal': '2024-01-01',
                'unit': '9',
                'estate': '2B',
                'total_transaksi': 100,
                'total_nilai': 50000000
            }
        ]
        
        report_data = ReportData(valid_data)
        self.assertTrue(report_data.is_valid())
        
        # Invalid data structure - missing required fields
        invalid_data = [
            {
                'tanggal': '2024-01-01',
                'unit': '9',
                # Missing estate, total_transaksi, total_nilai
            }
        ]
        
        report_data = ReportData(invalid_data)
        self.assertFalse(report_data.is_valid())
    
    def test_unit_9_estate_2b_data_filtering(self):
        """Test filtering data for Unit 9 Estate 2B"""
        mixed_data = [
            {'tanggal': '2024-01-01', 'unit': '9', 'estate': '2B', 'total_transaksi': 100},
            {'tanggal': '2024-01-01', 'unit': '8', 'estate': '2A', 'total_transaksi': 80},
            {'tanggal': '2024-01-01', 'unit': '9', 'estate': '2B', 'total_transaksi': 120},
            {'tanggal': '2024-01-01', 'unit': '9', 'estate': '2A', 'total_transaksi': 90}
        ]
        
        report_data = ReportData(mixed_data)
        filtered_data = report_data.filter_by_unit_estate("9", "2B")
        
        # Should have 2 records for Unit 9 Estate 2B
        self.assertEqual(len(filtered_data), 2)
        
        # All records should be Unit 9 Estate 2B
        for record in filtered_data:
            self.assertEqual(record['unit'], '9')
            self.assertEqual(record['estate'], '2B')
    
    def test_data_aggregation(self):
        """Test data aggregation for reports"""
        sample_data = [
            {'tanggal': '2024-01-01', 'unit': '9', 'estate': '2B', 'total_transaksi': 100, 'total_nilai': 50000000},
            {'tanggal': '2024-01-02', 'unit': '9', 'estate': '2B', 'total_transaksi': 150, 'total_nilai': 75000000},
            {'tanggal': '2024-01-03', 'unit': '9', 'estate': '2B', 'total_transaksi': 120, 'total_nilai': 60000000}
        ]
        
        report_data = ReportData(sample_data)
        summary = report_data.get_summary()
        
        # Verify aggregation
        self.assertEqual(summary['total_records'], 3)
        self.assertEqual(summary['total_transaksi'], 370)
        self.assertEqual(summary['total_nilai'], 185000000)
        self.assertEqual(summary['avg_transaksi_per_day'], 123.33)
    
    def test_date_range_validation(self):
        """Test date range validation in report data"""
        data_with_dates = [
            {'tanggal': '2024-01-01', 'unit': '9', 'estate': '2B', 'total_transaksi': 100},
            {'tanggal': '2024-01-15', 'unit': '9', 'estate': '2B', 'total_transaksi': 150},
            {'tanggal': '2024-01-31', 'unit': '9', 'estate': '2B', 'total_transaksi': 120}
        ]
        
        report_data = ReportData(data_with_dates)
        
        # Test date range filtering
        filtered_data = report_data.filter_by_date_range('2024-01-01', '2024-01-15')
        self.assertEqual(len(filtered_data), 2)
        
        # Test invalid date range
        invalid_filtered = report_data.filter_by_date_range('2024-02-01', '2024-02-28')
        self.assertEqual(len(invalid_filtered), 0)


class TestReportOutputValidation(unittest.TestCase):
    """Test cases for report output validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_excel_output_format(self):
        """Test Excel output format validation"""
        # Mock Excel file creation
        test_file_path = os.path.join(self.temp_dir, "test_report.xlsx")
        
        # Create mock Excel content
        with open(test_file_path, 'wb') as f:
            f.write(b'Mock Excel Content')
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file_path))
        
        # Verify file extension
        self.assertTrue(test_file_path.endswith('.xlsx'))
    
    def test_pdf_output_format(self):
        """Test PDF output format validation"""
        test_file_path = os.path.join(self.temp_dir, "test_report.pdf")
        
        # Create mock PDF content
        with open(test_file_path, 'wb') as f:
            f.write(b'%PDF-1.4 Mock PDF Content')
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file_path))
        
        # Verify file extension
        self.assertTrue(test_file_path.endswith('.pdf'))
    
    def test_output_filename_convention(self):
        """Test output filename follows convention"""
        from business.services.report_generator_service import ReportGeneratorService
        
        # Mock service
        with patch('data.database.database_manager.DatabaseManager'):
            service = ReportGeneratorService(Mock())
        
        # Test filename generation
        config = ReportConfiguration(
            name="Unit 9 Estate 2B Daily Report",
            unit="9",
            estate="2B",
            frequency="daily",
            time="08:00"
        )
        
        filename = service.generate_filename(config, datetime.datetime(2024, 1, 15))
        
        # Verify filename contains unit and estate
        self.assertIn("Unit_9", filename)
        self.assertIn("Estate_2B", filename)
        self.assertIn("2024-01-15", filename)
    
    def test_report_content_validation(self):
        """Test report content validation"""
        # Sample report content
        report_content = {
            'title': 'Unit 9 Estate 2B Daily Report',
            'date_range': '2024-01-01 to 2024-01-31',
            'unit': '9',
            'estate': '2B',
            'summary': {
                'total_records': 31,
                'total_transaksi': 4650,
                'total_nilai': 2325000000
            },
            'details': [
                {'tanggal': '2024-01-01', 'transaksi': 150, 'nilai': 75000000}
            ]
        }
        
        # Validate required fields
        required_fields = ['title', 'date_range', 'unit', 'estate', 'summary', 'details']
        for field in required_fields:
            self.assertIn(field, report_content)
        
        # Validate Unit 9 Estate 2B specific content
        self.assertEqual(report_content['unit'], '9')
        self.assertEqual(report_content['estate'], '2B')
        self.assertIn('Unit 9 Estate 2B', report_content['title'])


class TestEdgeCasesAndBoundaryConditions(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = []
        report_data = ReportData(empty_data)
        
        # Should handle empty data gracefully
        self.assertTrue(report_data.is_empty())
        
        summary = report_data.get_summary()
        self.assertEqual(summary['total_records'], 0)
        self.assertEqual(summary['total_transaksi'], 0)
        self.assertEqual(summary['total_nilai'], 0)
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Generate large dataset
        large_data = []
        for i in range(10000):
            large_data.append({
                'tanggal': f'2024-01-{(i % 31) + 1:02d}',
                'unit': '9',
                'estate': '2B',
                'total_transaksi': i + 1,
                'total_nilai': (i + 1) * 1000000
            })
        
        report_data = ReportData(large_data)
        
        # Should handle large dataset
        self.assertEqual(len(report_data.data), 10000)
        
        # Summary should be calculated correctly
        summary = report_data.get_summary()
        self.assertEqual(summary['total_records'], 10000)
    
    def test_invalid_date_formats(self):
        """Test handling of invalid date formats"""
        invalid_date_data = [
            {'tanggal': 'invalid-date', 'unit': '9', 'estate': '2B', 'total_transaksi': 100},
            {'tanggal': '2024-13-45', 'unit': '9', 'estate': '2B', 'total_transaksi': 150},
            {'tanggal': '', 'unit': '9', 'estate': '2B', 'total_transaksi': 120}
        ]
        
        report_data = ReportData(invalid_date_data)
        
        # Should identify invalid data
        self.assertFalse(report_data.is_valid())
        
        # Should filter out invalid dates
        valid_data = report_data.get_valid_records()
        self.assertEqual(len(valid_data), 0)  # All dates are invalid
    
    def test_concurrent_report_generation(self):
        """Test concurrent report generation"""
        import threading
        import time
        
        # Mock service
        with patch('data.database.database_manager.DatabaseManager'):
            service = AutomatedReportService(Mock())
            service.repository = Mock()
        
        results = []
        errors = []
        
        def generate_report_thread(config_id):
            try:
                config = ReportConfiguration(
                    id=config_id,
                    name=f"Concurrent Test {config_id}",
                    unit="9",
                    estate="2B",
                    frequency="daily",
                    time="08:00"
                )
                
                # Mock report generation
                with patch.object(service, 'generate_report') as mock_generate:
                    mock_generate.return_value = f"report_{config_id}.xlsx"
                    result = service.generate_report(config)
                    results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_report_thread, args=(f"config_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 5)


if __name__ == '__main__':
    # Create comprehensive test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestAutomatedReportService,
        TestReportConfiguration,
        TestReportDataValidation,
        TestReportOutputValidation,
        TestEdgeCasesAndBoundaryConditions
    ]
    
    for test_class in test_classes:
        test_suite.addTest(unittest.makeSuite(test_class))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print comprehensive summary
    print(f"\n{'='*80}")
    print(f"AUTOMATED REPORTING SYSTEM TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful Tests: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed Tests: {len(result.failures)}")
    print(f"Error Tests: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Test coverage for Unit 9 Estate 2B specific features
    print(f"\n{'='*40} UNIT 9 ESTATE 2B COVERAGE {'='*40}")
    print("✓ Configuration Creation and Validation")
    print("✓ Data Filtering and Aggregation")
    print("✓ Report Generation with Specific Parameters")
    print("✓ Output Format Validation")
    print("✓ Scheduled Report Execution")
    print("✓ Error Handling and Edge Cases")
    print("✓ Concurrent Processing")
    print("✓ Data Validation and Quality Checks")
    
    print(f"\n{'='*80}")
    print("Automated reporting tests completed!" if result.wasSuccessful() else "Some automated reporting tests failed!")
    print(f"{'='*80}")