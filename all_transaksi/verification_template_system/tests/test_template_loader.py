#!/usr/bin/env python3
"""
Unit tests for template loader module.
"""

import unittest
import tempfile
import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from verification_template_system.core.template_loader import TemplateLoader


class TestTemplateLoader(unittest.TestCase):
    """Test cases for TemplateLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(self.templates_dir)
        
        # Create test JSON template
        self.test_json_template = {
            "template_info": {
                "name": "test_template",
                "version": "1.0.0",
                "description": "Test template",
                "author": "Test Author",
                "created_date": "2024-01-01"
            },
            "sql_queries": {
                "employee_mapping": "SELECT EMP_ID, EMP_NAME FROM EMP"
            },
            "business_logic": {
                "verification_steps": ["step1", "step2"]
            },
            "output_format": {
                "type": "json",
                "fields": ["field1", "field2"]
            },
            "configuration": {
                "batch_size": 100,
                "timeout_seconds": 60
            },
            "validation_rules": {
                "required_fields": ["field1"]
            }
        }
        
        self.test_json_path = os.path.join(self.templates_dir, "test_template.json")
        with open(self.test_json_path, 'w') as f:
            json.dump(self.test_json_template, f)
        
        # Create test Python template
        self.test_py_template_content = '''
class TestTemplate:
    """Test template class."""
    
    def __init__(self, db_config, logger=None):
        self.db_config = db_config
        self.logger = logger
    
    def get_template_info(self):
        return {
            "name": "test_py_template",
            "version": "1.0.0",
            "description": "Test Python template",
            "author": "Test Author",
            "created_date": "2024-01-01"
        }
    
    def run_verification(self, estate_name, start_date, end_date, **kwargs):
        return {
            "success": True,
            "estate_name": estate_name,
            "start_date": start_date,
            "end_date": end_date,
            "data": {"test": "data"}
        }
'''
        
        self.test_py_path = os.path.join(self.templates_dir, "test_py_template.py")
        with open(self.test_py_path, 'w') as f:
            f.write(self.test_py_template_content)
        
        # Initialize template loader
        self.loader = TemplateLoader(templates_dir=self.templates_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_custom_dir(self):
        """Test TemplateLoader initialization with custom directory."""
        loader = TemplateLoader(templates_dir=self.templates_dir)
        self.assertEqual(str(loader.templates_dir), self.templates_dir)
    
    def test_init_with_default_dir(self):
        """Test TemplateLoader initialization with default directory."""
        with patch('pathlib.Path.exists', return_value=True):
            loader = TemplateLoader()
            self.assertTrue(str(loader.templates_dir).endswith('templates'))
    
    def test_scan_templates(self):
        """Test template scanning functionality."""
        templates = self.loader.scan_templates()
        
        self.assertIn('test_template', templates)
        self.assertIn('test_py_template', templates)
        self.assertEqual(len(templates), 2)
    
    def test_get_available_templates(self):
        """Test getting available templates."""
        templates = self.loader.get_available_templates()
        
        self.assertIsInstance(templates, list)
        self.assertIn('test_template', templates)
        self.assertIn('test_py_template', templates)
    
    def test_get_template_info_json(self):
        """Test getting template info from JSON template."""
        info = self.loader.get_template_info('test_template')
        
        self.assertEqual(info['name'], 'test_template')
        self.assertEqual(info['version'], '1.0.0')
        self.assertEqual(info['description'], 'Test template')
        self.assertEqual(info['author'], 'Test Author')
    
    def test_get_template_info_python(self):
        """Test getting template info from Python template."""
        info = self.loader.get_template_info('test_py_template')
        
        self.assertEqual(info['name'], 'test_py_template')
        self.assertEqual(info['version'], '1.0.0')
        self.assertEqual(info['description'], 'Test Python template')
    
    def test_get_template_info_not_found(self):
        """Test getting template info for non-existent template."""
        with self.assertRaises(FileNotFoundError):
            self.loader.get_template_info('non_existent_template')
    
    def test_load_json_template(self):
        """Test loading JSON template configuration."""
        config = self.loader.load_json_template('test_template')
        
        self.assertEqual(config['template_info']['name'], 'test_template')
        self.assertIn('sql_queries', config)
        self.assertIn('business_logic', config)
        self.assertIn('output_format', config)
    
    def test_load_json_template_not_found(self):
        """Test loading non-existent JSON template."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_json_template('non_existent_template')
    
    def test_load_python_template_class(self):
        """Test loading Python template class."""
        template_class = self.loader.load_python_template_class('test_py_template')
        
        self.assertIsNotNone(template_class)
        self.assertEqual(template_class.__name__, 'TestTemplate')
    
    def test_load_python_template_class_not_found(self):
        """Test loading non-existent Python template class."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_python_template_class('non_existent_template')
    
    def test_create_template_instance(self):
        """Test creating template instance."""
        mock_db_config = MagicMock()
        mock_logger = MagicMock()
        
        instance = self.loader.create_template_instance(
            'test_py_template',
            db_config=mock_db_config,
            logger=mock_logger
        )
        
        self.assertIsNotNone(instance)
        self.assertEqual(instance.db_config, mock_db_config)
        self.assertEqual(instance.logger, mock_logger)
    
    def test_create_template_instance_not_found(self):
        """Test creating instance for non-existent template."""
        with self.assertRaises(FileNotFoundError):
            self.loader.create_template_instance('non_existent_template')
    
    def test_validate_template_json_valid(self):
        """Test validating valid JSON template."""
        is_valid, errors = self.loader.validate_template('test_template')
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_template_python_valid(self):
        """Test validating valid Python template."""
        is_valid, errors = self.loader.validate_template('test_py_template')
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_template_missing_sections(self):
        """Test validating template with missing sections."""
        # Create invalid template
        invalid_template = {"template_info": {"name": "invalid"}}
        invalid_path = os.path.join(self.templates_dir, "invalid_template.json")
        
        with open(invalid_path, 'w') as f:
            json.dump(invalid_template, f)
        
        is_valid, errors = self.loader.validate_template('invalid_template')
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Clean up
        os.remove(invalid_path)
    
    def test_validate_template_not_found(self):
        """Test validating non-existent template."""
        is_valid, errors = self.loader.validate_template('non_existent_template')
        
        self.assertFalse(is_valid)
        self.assertIn("Template file not found", errors[0])
    
    def test_reload_templates(self):
        """Test reloading templates."""
        # Initial scan
        initial_templates = self.loader.get_available_templates()
        
        # Add new template
        new_template = {"template_info": {"name": "new_template"}}
        new_path = os.path.join(self.templates_dir, "new_template.json")
        
        with open(new_path, 'w') as f:
            json.dump(new_template, f)
        
        # Reload and check
        self.loader.reload_templates()
        updated_templates = self.loader.get_available_templates()
        
        self.assertGreater(len(updated_templates), len(initial_templates))
        self.assertIn('new_template', updated_templates)
        
        # Clean up
        os.remove(new_path)
    
    def test_get_template_type_json(self):
        """Test getting template type for JSON template."""
        template_type = self.loader._get_template_type('test_template')
        self.assertEqual(template_type, 'json')
    
    def test_get_template_type_python(self):
        """Test getting template type for Python template."""
        template_type = self.loader._get_template_type('test_py_template')
        self.assertEqual(template_type, 'python')
    
    def test_get_template_type_not_found(self):
        """Test getting template type for non-existent template."""
        template_type = self.loader._get_template_type('non_existent_template')
        self.assertIsNone(template_type)
    
    def test_validate_json_template_structure(self):
        """Test JSON template structure validation."""
        # Valid template
        is_valid, errors = self.loader._validate_json_template_structure(self.test_json_template)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid template - missing required section
        invalid_template = {"template_info": {"name": "test"}}
        is_valid, errors = self.loader._validate_json_template_structure(invalid_template)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_python_template_class(self):
        """Test Python template class validation."""
        template_class = self.loader.load_python_template_class('test_py_template')
        is_valid, errors = self.loader._validate_python_template_class(template_class)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_python_template_class_missing_methods(self):
        """Test Python template class validation with missing methods."""
        # Create class without required methods
        class IncompleteTemplate:
            pass
        
        is_valid, errors = self.loader._validate_python_template_class(IncompleteTemplate)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestTemplateLoaderIntegration(unittest.TestCase):
    """Integration tests for TemplateLoader."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(self.templates_dir)
        
        # Create a more realistic template
        self.realistic_template = {
            "template_info": {
                "name": "integration_test_template",
                "version": "1.0.0",
                "description": "Integration test template",
                "author": "Test Suite",
                "created_date": "2024-01-01"
            },
            "sql_queries": {
                "employee_mapping": "SELECT EMP_ID, EMP_NAME FROM EMP WHERE ESTATE = ?",
                "division_tables": "SELECT DISTINCT TABLE_NAME FROM RDB$RELATIONS WHERE TABLE_NAME LIKE 'FFBSCANNERDATA_%'",
                "granular_data": "SELECT * FROM {table_name} WHERE DIVISION = ? AND TRANSDATE BETWEEN ? AND ?"
            },
            "business_logic": {
                "verification_steps": [
                    "get_employee_mapping",
                    "get_divisions",
                    "analyze_divisions",
                    "calculate_totals"
                ],
                "duplicate_handling": {
                    "enabled": True,
                    "group_by": ["TRANSNO", "DIVISION"]
                },
                "calculations": {
                    "kerani": {
                        "based_on": "duplicates",
                        "fields": ["RIPEBCH", "UNRIPEBCH", "EMPTYBNCH", "LOOSEFRUIT"]
                    },
                    "mandor": {
                        "filter": "RECORDTAG == 'P1'",
                        "group_by": ["TRANSNO"]
                    }
                }
            },
            "output_format": {
                "type": "json",
                "structure": {
                    "summary": {
                        "total_employees": "int",
                        "total_divisions": "int",
                        "verification_rate": "float"
                    },
                    "details": {
                        "employees": "list",
                        "divisions": "list"
                    }
                }
            },
            "configuration": {
                "batch_size": 500,
                "timeout_seconds": 300,
                "retry_attempts": 3,
                "enable_logging": True
            },
            "validation_rules": {
                "required_fields": ["TRANSNO", "DIVISION", "TRANSDATE"],
                "date_format": "YYYY-MM-DD",
                "numeric_fields": ["RIPEBCH", "UNRIPEBCH", "EMPTYBNCH", "LOOSEFRUIT"]
            }
        }
        
        self.template_path = os.path.join(self.templates_dir, "integration_test_template.json")
        with open(self.template_path, 'w') as f:
            json.dump(self.realistic_template, f, indent=2)
        
        self.loader = TemplateLoader(templates_dir=self.templates_dir)
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_template_lifecycle(self):
        """Test complete template lifecycle: scan, load, validate."""
        # 1. Scan templates
        templates = self.loader.scan_templates()
        self.assertIn('integration_test_template', templates)
        
        # 2. Get template info
        info = self.loader.get_template_info('integration_test_template')
        self.assertEqual(info['name'], 'integration_test_template')
        self.assertEqual(info['description'], 'Integration test template')
        
        # 3. Load template configuration
        config = self.loader.load_json_template('integration_test_template')
        self.assertIn('sql_queries', config)
        self.assertIn('business_logic', config)
        
        # 4. Validate template
        is_valid, errors = self.loader.validate_template('integration_test_template')
        self.assertTrue(is_valid, f"Template validation failed: {errors}")
        
        # 5. Reload templates
        self.loader.reload_templates()
        updated_templates = self.loader.get_available_templates()
        self.assertIn('integration_test_template', updated_templates)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestTemplateLoader))
    suite.addTest(unittest.makeSuite(TestTemplateLoaderIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)