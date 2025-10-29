#!/usr/bin/env python3
"""
Unit tests for database configuration module.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from verification_template_system.config.database_config import DatabaseConfig


class TestDatabaseConfig(unittest.TestCase):
    """Test cases for DatabaseConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.temp_dir, "test_config.json")
        self.test_db_path = os.path.join(self.temp_dir, "test.fdb")
        
        # Create test config file
        self.test_config_data = {
            "Test Estate": self.test_db_path
        }
        
        with open(self.test_config_path, 'w') as f:
            json.dump(self.test_config_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_valid_params(self):
        """Test DatabaseConfig initialization with valid parameters."""
        config = DatabaseConfig(
            estate_name="Test Estate",
            database_path=self.test_db_path,
            host="localhost",
            port=3050,
            username="SYSDBA",
            password="masterkey",
            charset="UTF8"
        )
        
        self.assertEqual(config.estate_name, "Test Estate")
        self.assertEqual(config.database_path, self.test_db_path)
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 3050)
        self.assertEqual(config.username, "SYSDBA")
        self.assertEqual(config.password, "masterkey")
        self.assertEqual(config.charset, "UTF8")
    
    def test_init_with_minimal_params(self):
        """Test DatabaseConfig initialization with minimal parameters."""
        config = DatabaseConfig(
            estate_name="Test Estate",
            database_path=self.test_db_path
        )
        
        self.assertEqual(config.estate_name, "Test Estate")
        self.assertEqual(config.database_path, self.test_db_path)
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 3050)
        self.assertEqual(config.username, "SYSDBA")
        self.assertEqual(config.password, "masterkey")
        self.assertEqual(config.charset, "UTF8")
    
    def test_load_from_config_success(self):
        """Test successful loading from config file."""
        config = DatabaseConfig.load_from_config(self.test_config_path)
        
        self.assertEqual(config.estate_name, "Test Estate")
        self.assertEqual(config.database_path, self.test_db_path)
    
    def test_load_from_config_file_not_found(self):
        """Test loading from non-existent config file."""
        with self.assertRaises(FileNotFoundError):
            DatabaseConfig.load_from_config("non_existent_config.json")
    
    def test_load_from_config_invalid_json(self):
        """Test loading from invalid JSON file."""
        invalid_config_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_config_path, 'w') as f:
            f.write("invalid json content")
        
        with self.assertRaises(json.JSONDecodeError):
            DatabaseConfig.load_from_config(invalid_config_path)
    
    def test_load_from_config_empty_config(self):
        """Test loading from empty config file."""
        empty_config_path = os.path.join(self.temp_dir, "empty.json")
        with open(empty_config_path, 'w') as f:
            json.dump({}, f)
        
        with self.assertRaises(ValueError):
            DatabaseConfig.load_from_config(empty_config_path)
    
    def test_create_template_config(self):
        """Test creating template config file."""
        template_path = os.path.join(self.temp_dir, "template.json")
        DatabaseConfig.create_template_config(template_path)
        
        self.assertTrue(os.path.exists(template_path))
        
        with open(template_path, 'r') as f:
            template_data = json.load(f)
        
        self.assertIn("Estate Name 1", template_data)
        self.assertIn("Estate Name 2", template_data)
    
    def test_validate_database_path_exists(self):
        """Test database path validation when file exists."""
        # Create a dummy database file
        with open(self.test_db_path, 'w') as f:
            f.write("dummy content")
        
        config = DatabaseConfig("Test Estate", self.test_db_path)
        self.assertTrue(config.validate_database_path())
    
    def test_validate_database_path_not_exists(self):
        """Test database path validation when file doesn't exist."""
        config = DatabaseConfig("Test Estate", "non_existent.fdb")
        self.assertFalse(config.validate_database_path())
    
    def test_get_connection_string(self):
        """Test connection string generation."""
        config = DatabaseConfig(
            estate_name="Test Estate",
            database_path=self.test_db_path,
            host="testhost",
            port=3051,
            username="testuser",
            password="testpass",
            charset="WIN1252"
        )
        
        conn_str = config.get_connection_string()
        expected = f"testhost/3051:{self.test_db_path}"
        self.assertEqual(conn_str, expected)
    
    @patch('fdb.connect')
    def test_test_connection_success(self, mock_connect):
        """Test successful database connection test."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        config = DatabaseConfig("Test Estate", self.test_db_path)
        result = config.test_connection()
        
        self.assertTrue(result)
        mock_connect.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('fdb.connect')
    def test_test_connection_failure(self, mock_connect):
        """Test failed database connection test."""
        mock_connect.side_effect = Exception("Connection failed")
        
        config = DatabaseConfig("Test Estate", self.test_db_path)
        result = config.test_connection()
        
        self.assertFalse(result)
        mock_connect.assert_called_once()
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = DatabaseConfig(
            estate_name="Test Estate",
            database_path=self.test_db_path,
            host="testhost",
            port=3051
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict['estate_name'], "Test Estate")
        self.assertEqual(config_dict['database_path'], self.test_db_path)
        self.assertEqual(config_dict['host'], "testhost")
        self.assertEqual(config_dict['port'], 3051)
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            'estate_name': "Test Estate",
            'database_path': self.test_db_path,
            'host': "testhost",
            'port': 3051,
            'username': "testuser",
            'password': "testpass",
            'charset': "WIN1252"
        }
        
        config = DatabaseConfig.from_dict(config_dict)
        
        self.assertEqual(config.estate_name, "Test Estate")
        self.assertEqual(config.database_path, self.test_db_path)
        self.assertEqual(config.host, "testhost")
        self.assertEqual(config.port, 3051)
        self.assertEqual(config.username, "testuser")
        self.assertEqual(config.password, "testpass")
        self.assertEqual(config.charset, "WIN1252")
    
    def test_str_representation(self):
        """Test string representation."""
        config = DatabaseConfig("Test Estate", self.test_db_path)
        str_repr = str(config)
        
        self.assertIn("Test Estate", str_repr)
        self.assertIn(self.test_db_path, str_repr)
    
    def test_repr_representation(self):
        """Test repr representation."""
        config = DatabaseConfig("Test Estate", self.test_db_path)
        repr_str = repr(config)
        
        self.assertIn("DatabaseConfig", repr_str)
        self.assertIn("Test Estate", repr_str)


class TestVerificationTemplates(unittest.TestCase):
    """Test cases for VERIFICATION_TEMPLATES constant."""
    
    def test_verification_templates_structure(self):
        """Test that VERIFICATION_TEMPLATES has correct structure."""
        from verification_template_system.config.database_config import VERIFICATION_TEMPLATES
        
        self.assertIsInstance(VERIFICATION_TEMPLATES, dict)
        self.assertIn('transaction_verification', VERIFICATION_TEMPLATES)
        
        # Test transaction_verification template structure
        tx_template = VERIFICATION_TEMPLATES['transaction_verification']
        self.assertIn('description', tx_template)
        self.assertIn('required_tables', tx_template)
        self.assertIn('date_range_required', tx_template)
        self.assertIn('output_format', tx_template)
        
        # Test required_tables structure
        required_tables = tx_template['required_tables']
        self.assertIn('EMP', required_tables)
        self.assertIn('FFBSCANNERDATA_*', required_tables)
        
        # Test that it's boolean
        self.assertIsInstance(tx_template['date_range_required'], bool)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestDatabaseConfig))
    suite.addTest(unittest.makeSuite(TestVerificationTemplates))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)