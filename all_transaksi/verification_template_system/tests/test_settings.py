#!/usr/bin/env python3
"""
Unit tests for settings configuration module.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from verification_template_system.config.settings import (
    Settings, DevelopmentSettings, ProductionSettings, get_settings
)


class TestSettings(unittest.TestCase):
    """Test cases for Settings class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings = Settings(base_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_default(self):
        """Test Settings initialization with default values."""
        settings = Settings()
        
        # Check default paths
        self.assertIsNotNone(settings.BASE_DIR)
        self.assertIsNotNone(settings.TEMPLATES_DIR)
        self.assertIsNotNone(settings.LOGS_DIR)
        self.assertIsNotNone(settings.REPORTS_DIR)
        
        # Check default logging config
        self.assertEqual(settings.LOGGING_LEVEL, 'INFO')
        self.assertEqual(settings.LOGGING_FORMAT, 'detailed')
        self.assertTrue(settings.LOGGING_TO_FILE)
        self.assertTrue(settings.LOGGING_TO_CONSOLE)
        
        # Check default database config
        self.assertEqual(settings.DATABASE_TIMEOUT, 30)
        self.assertEqual(settings.DATABASE_RETRY_ATTEMPTS, 3)
        
        # Check default verification config
        self.assertEqual(settings.VERIFICATION_BATCH_SIZE, 1000)
        self.assertEqual(settings.VERIFICATION_RETRY_ATTEMPTS, 2)
        self.assertEqual(settings.VERIFICATION_SPECIAL_MONTHS, [1, 2, 3])
        self.assertIsInstance(settings.VERIFICATION_COMPARISON_FIELDS, list)
        self.assertIsInstance(settings.VERIFICATION_RECORD_TAGS, dict)
    
    def test_init_custom_base_dir(self):
        """Test Settings initialization with custom base directory."""
        custom_dir = os.path.join(self.temp_dir, "custom")
        settings = Settings(base_dir=custom_dir)
        
        self.assertEqual(settings.BASE_DIR, custom_dir)
        self.assertEqual(settings.TEMPLATES_DIR, os.path.join(custom_dir, "templates"))
        self.assertEqual(settings.LOGS_DIR, os.path.join(custom_dir, "logs"))
        self.assertEqual(settings.REPORTS_DIR, os.path.join(custom_dir, "reports"))
    
    def test_ensure_directories(self):
        """Test directory creation."""
        # Directories should not exist initially
        self.assertFalse(os.path.exists(self.settings.TEMPLATES_DIR))
        self.assertFalse(os.path.exists(self.settings.LOGS_DIR))
        self.assertFalse(os.path.exists(self.settings.REPORTS_DIR))
        
        # Ensure directories
        self.settings.ensure_directories()
        
        # Directories should now exist
        self.assertTrue(os.path.exists(self.settings.TEMPLATES_DIR))
        self.assertTrue(os.path.exists(self.settings.LOGS_DIR))
        self.assertTrue(os.path.exists(self.settings.REPORTS_DIR))
    
    def test_get_template_path(self):
        """Test getting template path."""
        template_name = "test_template"
        expected_path = os.path.join(self.settings.TEMPLATES_DIR, f"{template_name}.json")
        
        actual_path = self.settings.get_template_path(template_name)
        self.assertEqual(actual_path, expected_path)
    
    def test_get_template_path_with_extension(self):
        """Test getting template path with extension."""
        template_name = "test_template.json"
        expected_path = os.path.join(self.settings.TEMPLATES_DIR, template_name)
        
        actual_path = self.settings.get_template_path(template_name)
        self.assertEqual(actual_path, expected_path)
    
    def test_get_log_path(self):
        """Test getting log path."""
        log_name = "verification"
        expected_path = os.path.join(self.settings.LOGS_DIR, f"{log_name}.log")
        
        actual_path = self.settings.get_log_path(log_name)
        self.assertEqual(actual_path, expected_path)
    
    def test_get_log_path_with_extension(self):
        """Test getting log path with extension."""
        log_name = "verification.log"
        expected_path = os.path.join(self.settings.LOGS_DIR, log_name)
        
        actual_path = self.settings.get_log_path(log_name)
        self.assertEqual(actual_path, expected_path)
    
    def test_get_report_path(self):
        """Test getting report path."""
        report_name = "monthly_report"
        expected_path = os.path.join(self.settings.REPORTS_DIR, f"{report_name}.json")
        
        actual_path = self.settings.get_report_path(report_name)
        self.assertEqual(actual_path, expected_path)
    
    def test_get_report_path_with_extension(self):
        """Test getting report path with extension."""
        report_name = "monthly_report.xlsx"
        expected_path = os.path.join(self.settings.REPORTS_DIR, report_name)
        
        actual_path = self.settings.get_report_path(report_name)
        self.assertEqual(actual_path, expected_path)
    
    def test_verification_comparison_fields(self):
        """Test verification comparison fields structure."""
        fields = self.settings.VERIFICATION_COMPARISON_FIELDS
        
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)
        
        # Check that all fields are strings
        for field in fields:
            self.assertIsInstance(field, str)
    
    def test_verification_record_tags(self):
        """Test verification record tags structure."""
        tags = self.settings.VERIFICATION_RECORD_TAGS
        
        self.assertIsInstance(tags, dict)
        self.assertIn('kerani', tags)
        self.assertIn('mandor', tags)
        self.assertIn('asisten', tags)
        
        # Check tag values
        for tag_name, tag_values in tags.items():
            self.assertIsInstance(tag_values, list)
            for tag_value in tag_values:
                self.assertIsInstance(tag_value, str)


class TestDevelopmentSettings(unittest.TestCase):
    """Test cases for DevelopmentSettings class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings = DevelopmentSettings(base_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_development_specific_settings(self):
        """Test development-specific settings."""
        # Should inherit from base Settings
        self.assertIsInstance(self.settings, Settings)
        
        # Development-specific overrides
        self.assertEqual(self.settings.LOGGING_LEVEL, 'DEBUG')
        self.assertTrue(self.settings.LOGGING_TO_CONSOLE)
        self.assertEqual(self.settings.VERIFICATION_BATCH_SIZE, 100)  # Smaller for dev
        
        # Should have debug flag
        self.assertTrue(hasattr(self.settings, 'DEBUG'))
        self.assertTrue(self.settings.DEBUG)
    
    def test_development_directories(self):
        """Test development directory structure."""
        # Should have additional dev directories
        self.assertTrue(hasattr(self.settings, 'DEV_DATA_DIR'))
        self.assertTrue(hasattr(self.settings, 'TEST_REPORTS_DIR'))
        
        # Ensure directories
        self.settings.ensure_directories()
        
        # Check that dev directories are created
        self.assertTrue(os.path.exists(self.settings.DEV_DATA_DIR))
        self.assertTrue(os.path.exists(self.settings.TEST_REPORTS_DIR))


class TestProductionSettings(unittest.TestCase):
    """Test cases for ProductionSettings class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings = ProductionSettings(base_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_production_specific_settings(self):
        """Test production-specific settings."""
        # Should inherit from base Settings
        self.assertIsInstance(self.settings, Settings)
        
        # Production-specific overrides
        self.assertEqual(self.settings.LOGGING_LEVEL, 'WARNING')
        self.assertEqual(self.settings.LOGGING_FORMAT, 'json')
        self.assertEqual(self.settings.VERIFICATION_BATCH_SIZE, 5000)  # Larger for prod
        self.assertEqual(self.settings.DATABASE_TIMEOUT, 60)  # Longer timeout
        
        # Should have debug flag set to False
        self.assertTrue(hasattr(self.settings, 'DEBUG'))
        self.assertFalse(self.settings.DEBUG)
    
    def test_production_performance_settings(self):
        """Test production performance settings."""
        # Should have performance-oriented settings
        self.assertTrue(hasattr(self.settings, 'ENABLE_CACHING'))
        self.assertTrue(self.settings.ENABLE_CACHING)
        
        self.assertTrue(hasattr(self.settings, 'CACHE_SIZE'))
        self.assertGreater(self.settings.CACHE_SIZE, 0)
        
        self.assertTrue(hasattr(self.settings, 'MAX_CONCURRENT_VERIFICATIONS'))
        self.assertGreater(self.settings.MAX_CONCURRENT_VERIFICATIONS, 0)


class TestGetSettings(unittest.TestCase):
    """Test cases for get_settings function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.dict(os.environ, {'VERIFICATION_ENV': 'development'})
    def test_get_development_settings(self):
        """Test getting development settings."""
        settings = get_settings(base_dir=self.temp_dir)
        
        self.assertIsInstance(settings, DevelopmentSettings)
        self.assertEqual(settings.LOGGING_LEVEL, 'DEBUG')
        self.assertTrue(settings.DEBUG)
    
    @patch.dict(os.environ, {'VERIFICATION_ENV': 'production'})
    def test_get_production_settings(self):
        """Test getting production settings."""
        settings = get_settings(base_dir=self.temp_dir)
        
        self.assertIsInstance(settings, ProductionSettings)
        self.assertEqual(settings.LOGGING_LEVEL, 'WARNING')
        self.assertFalse(settings.DEBUG)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_default_settings(self):
        """Test getting default settings when no environment is set."""
        settings = get_settings(base_dir=self.temp_dir)
        
        # Should default to base Settings class
        self.assertEqual(type(settings), Settings)
        self.assertEqual(settings.LOGGING_LEVEL, 'INFO')
    
    @patch.dict(os.environ, {'VERIFICATION_ENV': 'invalid_env'})
    def test_get_settings_invalid_environment(self):
        """Test getting settings with invalid environment."""
        settings = get_settings(base_dir=self.temp_dir)
        
        # Should default to base Settings class
        self.assertEqual(type(settings), Settings)
        self.assertEqual(settings.LOGGING_LEVEL, 'INFO')


class TestSettingsIntegration(unittest.TestCase):
    """Integration tests for settings functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_settings_workflow(self):
        """Test complete settings workflow."""
        # Create settings
        settings = Settings(base_dir=self.temp_dir)
        
        # Ensure directories
        settings.ensure_directories()
        
        # Test path generation
        template_path = settings.get_template_path("test_template")
        log_path = settings.get_log_path("verification")
        report_path = settings.get_report_path("monthly_report")
        
        # Verify paths are correct
        self.assertTrue(template_path.startswith(settings.TEMPLATES_DIR))
        self.assertTrue(log_path.startswith(settings.LOGS_DIR))
        self.assertTrue(report_path.startswith(settings.REPORTS_DIR))
        
        # Verify directories exist
        self.assertTrue(os.path.exists(settings.TEMPLATES_DIR))
        self.assertTrue(os.path.exists(settings.LOGS_DIR))
        self.assertTrue(os.path.exists(settings.REPORTS_DIR))
    
    @patch.dict(os.environ, {'VERIFICATION_ENV': 'development'})
    def test_environment_specific_workflow(self):
        """Test environment-specific settings workflow."""
        # Get development settings
        dev_settings = get_settings(base_dir=self.temp_dir)
        
        # Verify it's development settings
        self.assertIsInstance(dev_settings, DevelopmentSettings)
        self.assertTrue(dev_settings.DEBUG)
        
        # Ensure directories (including dev-specific ones)
        dev_settings.ensure_directories()
        
        # Verify all directories exist
        self.assertTrue(os.path.exists(dev_settings.TEMPLATES_DIR))
        self.assertTrue(os.path.exists(dev_settings.LOGS_DIR))
        self.assertTrue(os.path.exists(dev_settings.REPORTS_DIR))
        self.assertTrue(os.path.exists(dev_settings.DEV_DATA_DIR))
        self.assertTrue(os.path.exists(dev_settings.TEST_REPORTS_DIR))
    
    def test_settings_consistency(self):
        """Test settings consistency across different environments."""
        base_settings = Settings(base_dir=self.temp_dir)
        dev_settings = DevelopmentSettings(base_dir=self.temp_dir)
        prod_settings = ProductionSettings(base_dir=self.temp_dir)
        
        # All should have the same base directory structure
        self.assertEqual(base_settings.BASE_DIR, dev_settings.BASE_DIR)
        self.assertEqual(base_settings.BASE_DIR, prod_settings.BASE_DIR)
        
        # All should have the same core directories
        self.assertEqual(base_settings.TEMPLATES_DIR, dev_settings.TEMPLATES_DIR)
        self.assertEqual(base_settings.TEMPLATES_DIR, prod_settings.TEMPLATES_DIR)
        
        # All should have verification comparison fields
        self.assertEqual(
            base_settings.VERIFICATION_COMPARISON_FIELDS,
            dev_settings.VERIFICATION_COMPARISON_FIELDS
        )
        self.assertEqual(
            base_settings.VERIFICATION_COMPARISON_FIELDS,
            prod_settings.VERIFICATION_COMPARISON_FIELDS
        )
        
        # All should have verification record tags
        self.assertEqual(
            base_settings.VERIFICATION_RECORD_TAGS,
            dev_settings.VERIFICATION_RECORD_TAGS
        )
        self.assertEqual(
            base_settings.VERIFICATION_RECORD_TAGS,
            prod_settings.VERIFICATION_RECORD_TAGS
        )


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestSettings))
    suite.addTest(unittest.makeSuite(TestDevelopmentSettings))
    suite.addTest(unittest.makeSuite(TestProductionSettings))
    suite.addTest(unittest.makeSuite(TestGetSettings))
    suite.addTest(unittest.makeSuite(TestSettingsIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)