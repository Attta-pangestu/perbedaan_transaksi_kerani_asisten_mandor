#!/usr/bin/env python3
"""
Unit tests for verification engine module.
"""

import unittest
import tempfile
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from verification_template_system.core.verification_engine import VerificationEngine, VerificationBatch
from verification_template_system.config.database_config import DatabaseConfig


class TestVerificationEngine(unittest.TestCase):
    """Test cases for VerificationEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(self.templates_dir)
        
        # Create mock database config
        self.mock_db_config = MagicMock(spec=DatabaseConfig)
        self.mock_db_config.estate_name = "Test Estate"
        self.mock_db_config.database_path = "/path/to/test.fdb"
        self.mock_db_config.test_connection.return_value = True
        
        # Create test template
        self.test_template = {
            "template_info": {
                "name": "test_template",
                "version": "1.0.0",
                "description": "Test template",
                "author": "Test Author"
            },
            "sql_queries": {
                "employee_mapping": "SELECT EMP_ID, EMP_NAME FROM EMP"
            },
            "business_logic": {
                "verification_steps": ["step1", "step2"]
            },
            "output_format": {
                "type": "json"
            },
            "configuration": {
                "batch_size": 100
            },
            "validation_rules": {
                "required_fields": ["field1"]
            }
        }
        
        template_path = os.path.join(self.templates_dir, "test_template.json")
        with open(template_path, 'w') as f:
            json.dump(self.test_template, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_db_config(self):
        """Test VerificationEngine initialization with database config."""
        engine = VerificationEngine(
            db_config=self.mock_db_config,
            templates_dir=self.templates_dir,
            verbose=True
        )
        
        self.assertEqual(engine.db_config, self.mock_db_config)
        self.assertTrue(engine.verbose)
        self.assertIsNotNone(engine.template_loader)
        self.assertIsNotNone(engine.logger)
    
    def test_init_without_db_config(self):
        """Test VerificationEngine initialization without database config."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        
        self.assertIsNone(engine.db_config)
        self.assertIsNotNone(engine.template_loader)
        self.assertIsNotNone(engine.logger)
    
    def test_get_available_templates(self):
        """Test getting available templates."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        templates = engine.get_available_templates()
        
        self.assertIsInstance(templates, list)
        self.assertIn('test_template', templates)
    
    def test_load_template_success(self):
        """Test successful template loading."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        template = engine.load_template('test_template')
        
        self.assertIsNotNone(template)
        self.assertEqual(template['template_info']['name'], 'test_template')
    
    def test_load_template_not_found(self):
        """Test loading non-existent template."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        
        with self.assertRaises(FileNotFoundError):
            engine.load_template('non_existent_template')
    
    def test_validate_template_success(self):
        """Test successful template validation."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        is_valid = engine.validate_template('test_template')
        
        self.assertTrue(is_valid)
    
    def test_validate_template_failure(self):
        """Test template validation failure."""
        # Create invalid template
        invalid_template = {"template_info": {"name": "invalid"}}
        invalid_path = os.path.join(self.templates_dir, "invalid_template.json")
        
        with open(invalid_path, 'w') as f:
            json.dump(invalid_template, f)
        
        engine = VerificationEngine(templates_dir=self.templates_dir)
        is_valid = engine.validate_template('invalid_template')
        
        self.assertFalse(is_valid)
        
        # Clean up
        os.remove(invalid_path)
    
    def test_prepare_verification_with_db_config(self):
        """Test verification preparation with database config."""
        engine = VerificationEngine(
            db_config=self.mock_db_config,
            templates_dir=self.templates_dir
        )
        
        result = engine.prepare_verification('test_template')
        
        self.assertTrue(result['success'])
        self.assertIn('template', result)
        self.assertIn('db_config', result)
    
    def test_prepare_verification_without_db_config(self):
        """Test verification preparation without database config."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        
        result = engine.prepare_verification('test_template')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_prepare_verification_invalid_template(self):
        """Test verification preparation with invalid template."""
        engine = VerificationEngine(
            db_config=self.mock_db_config,
            templates_dir=self.templates_dir
        )
        
        result = engine.prepare_verification('non_existent_template')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('verification_template_system.templates.transaction_verification.TransactionVerificationTemplate')
    def test_run_verification_success(self, mock_template_class):
        """Test successful verification run."""
        # Setup mock template instance
        mock_template_instance = MagicMock()
        mock_template_instance.run_verification.return_value = {
            'success': True,
            'estate_name': 'Test Estate',
            'data': {'test': 'result'}
        }
        mock_template_class.return_value = mock_template_instance
        
        # Create Python template file
        py_template_content = '''
class TestTemplate:
    def __init__(self, db_config, logger=None):
        self.db_config = db_config
        self.logger = logger
    
    def run_verification(self, estate_name, start_date, end_date, **kwargs):
        return {
            'success': True,
            'estate_name': estate_name,
            'data': {'test': 'result'}
        }
'''
        py_template_path = os.path.join(self.templates_dir, "test_template.py")
        with open(py_template_path, 'w') as f:
            f.write(py_template_content)
        
        engine = VerificationEngine(
            db_config=self.mock_db_config,
            templates_dir=self.templates_dir
        )
        
        result = engine.run_verification(
            template_name='test_template',
            estate_name='Test Estate',
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['estate_name'], 'Test Estate')
        
        # Clean up
        os.remove(py_template_path)
    
    def test_run_verification_preparation_failure(self):
        """Test verification run with preparation failure."""
        engine = VerificationEngine(templates_dir=self.templates_dir)  # No db_config
        
        result = engine.run_verification(
            template_name='test_template',
            estate_name='Test Estate',
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_save_results_success(self):
        """Test successful results saving."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        
        test_results = {
            'success': True,
            'estate_name': 'Test Estate',
            'data': {'test': 'result'}
        }
        
        output_file = os.path.join(self.temp_dir, "test_results.json")
        success = engine.save_results(test_results, output_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify content
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['estate_name'], 'Test Estate')
    
    def test_save_results_failure(self):
        """Test results saving failure."""
        engine = VerificationEngine(templates_dir=self.templates_dir)
        
        test_results = {'test': 'data'}
        invalid_path = "/invalid/path/results.json"
        
        success = engine.save_results(test_results, invalid_path)
        self.assertFalse(success)
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        engine = VerificationEngine(
            db_config=self.mock_db_config,
            templates_dir=self.templates_dir
        )
        
        # Should not raise any exceptions
        engine.cleanup()
        
        # Verify cleanup was called
        self.assertIsNone(engine.db_config)


class TestVerificationBatch(unittest.TestCase):
    """Test cases for VerificationBatch class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.batch = VerificationBatch()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test VerificationBatch initialization."""
        batch = VerificationBatch()
        
        self.assertEqual(len(batch.jobs), 0)
        self.assertIsNotNone(batch.logger)
    
    def test_add_job(self):
        """Test adding a job to the batch."""
        job_id = self.batch.add_job(
            template_name='test_template',
            estate_name='Test Estate',
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        self.assertIsNotNone(job_id)
        self.assertEqual(len(self.batch.jobs), 1)
        
        job = self.batch.jobs[0]
        self.assertEqual(job['template_name'], 'test_template')
        self.assertEqual(job['estate_name'], 'Test Estate')
        self.assertEqual(job['start_date'], '2024-01-01')
        self.assertEqual(job['end_date'], '2024-01-31')
    
    def test_add_job_with_custom_config(self):
        """Test adding a job with custom configuration."""
        custom_config = {'batch_size': 200, 'timeout': 300}
        
        job_id = self.batch.add_job(
            template_name='test_template',
            estate_name='Test Estate',
            start_date='2024-01-01',
            end_date='2024-01-31',
            custom_config=custom_config
        )
        
        job = self.batch.jobs[0]
        self.assertEqual(job['custom_config'], custom_config)
    
    def test_get_jobs(self):
        """Test getting all jobs."""
        # Add multiple jobs
        self.batch.add_job('template1', 'Estate1', '2024-01-01', '2024-01-31')
        self.batch.add_job('template2', 'Estate2', '2024-02-01', '2024-02-28')
        
        jobs = self.batch.get_jobs()
        
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['template_name'], 'template1')
        self.assertEqual(jobs[1]['template_name'], 'template2')
    
    def test_clear_jobs(self):
        """Test clearing all jobs."""
        # Add jobs
        self.batch.add_job('template1', 'Estate1', '2024-01-01', '2024-01-31')
        self.batch.add_job('template2', 'Estate2', '2024-02-01', '2024-02-28')
        
        self.assertEqual(len(self.batch.jobs), 2)
        
        # Clear jobs
        self.batch.clear_jobs()
        
        self.assertEqual(len(self.batch.jobs), 0)
    
    @patch('verification_template_system.core.verification_engine.VerificationEngine')
    def test_run_all_success(self, mock_engine_class):
        """Test successful batch execution."""
        # Setup mock engine
        mock_engine = MagicMock()
        mock_engine.run_verification.return_value = {
            'success': True,
            'job_id': 'test_job_1',
            'data': {'test': 'result'}
        }
        mock_engine_class.return_value = mock_engine
        
        # Add jobs
        job_id1 = self.batch.add_job('template1', 'Estate1', '2024-01-01', '2024-01-31')
        job_id2 = self.batch.add_job('template2', 'Estate2', '2024-02-01', '2024-02-28')
        
        # Run batch
        results = self.batch.run_all()
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))
        
        # Verify engine was called correctly
        self.assertEqual(mock_engine.run_verification.call_count, 2)
    
    @patch('verification_template_system.core.verification_engine.VerificationEngine')
    def test_run_all_with_failures(self, mock_engine_class):
        """Test batch execution with some failures."""
        # Setup mock engine with mixed results
        mock_engine = MagicMock()
        mock_engine.run_verification.side_effect = [
            {'success': True, 'data': {'test': 'result1'}},
            {'success': False, 'error': 'Test error'},
            {'success': True, 'data': {'test': 'result3'}}
        ]
        mock_engine_class.return_value = mock_engine
        
        # Add jobs
        self.batch.add_job('template1', 'Estate1', '2024-01-01', '2024-01-31')
        self.batch.add_job('template2', 'Estate2', '2024-02-01', '2024-02-28')
        self.batch.add_job('template3', 'Estate3', '2024-03-01', '2024-03-31')
        
        # Run batch
        results = self.batch.run_all()
        
        self.assertEqual(len(results), 3)
        
        # Check results
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        self.assertEqual(len(successful_results), 2)
        self.assertEqual(len(failed_results), 1)
        self.assertEqual(failed_results[0]['error'], 'Test error')
    
    @patch('verification_template_system.core.verification_engine.VerificationEngine')
    def test_run_all_empty_batch(self, mock_engine_class):
        """Test running empty batch."""
        results = self.batch.run_all()
        
        self.assertEqual(len(results), 0)
        mock_engine_class.assert_not_called()
    
    def test_get_batch_summary(self):
        """Test getting batch summary."""
        # Add jobs
        self.batch.add_job('template1', 'Estate1', '2024-01-01', '2024-01-31')
        self.batch.add_job('template2', 'Estate2', '2024-02-01', '2024-02-28')
        
        summary = self.batch.get_batch_summary()
        
        self.assertEqual(summary['total_jobs'], 2)
        self.assertIn('jobs', summary)
        self.assertEqual(len(summary['jobs']), 2)


class TestVerificationEngineIntegration(unittest.TestCase):
    """Integration tests for VerificationEngine."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(self.templates_dir)
        
        # Create realistic template
        self.realistic_template = {
            "template_info": {
                "name": "integration_template",
                "version": "1.0.0",
                "description": "Integration test template",
                "author": "Test Suite"
            },
            "sql_queries": {
                "employee_mapping": "SELECT EMP_ID, EMP_NAME FROM EMP WHERE ESTATE = ?",
                "division_tables": "SELECT TABLE_NAME FROM RDB$RELATIONS WHERE TABLE_NAME LIKE 'FFBSCANNERDATA_%'"
            },
            "business_logic": {
                "verification_steps": ["get_employees", "analyze_data"],
                "calculations": {
                    "verification_rate": "calculated_field"
                }
            },
            "output_format": {
                "type": "json",
                "structure": {
                    "summary": {"total_employees": "int"},
                    "details": {"employees": "list"}
                }
            },
            "configuration": {
                "batch_size": 100,
                "timeout_seconds": 60
            },
            "validation_rules": {
                "required_fields": ["EMP_ID", "EMP_NAME"]
            }
        }
        
        template_path = os.path.join(self.templates_dir, "integration_template.json")
        with open(template_path, 'w') as f:
            json.dump(self.realistic_template, f, indent=2)
        
        # Mock database config
        self.mock_db_config = MagicMock(spec=DatabaseConfig)
        self.mock_db_config.estate_name = "Integration Test Estate"
        self.mock_db_config.database_path = "/path/to/integration_test.fdb"
        self.mock_db_config.test_connection.return_value = True
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_verification_workflow(self):
        """Test complete verification workflow."""
        engine = VerificationEngine(
            db_config=self.mock_db_config,
            templates_dir=self.templates_dir,
            verbose=True
        )
        
        # 1. Check available templates
        templates = engine.get_available_templates()
        self.assertIn('integration_template', templates)
        
        # 2. Validate template
        is_valid = engine.validate_template('integration_template')
        self.assertTrue(is_valid)
        
        # 3. Load template
        template = engine.load_template('integration_template')
        self.assertIsNotNone(template)
        
        # 4. Prepare verification
        preparation = engine.prepare_verification('integration_template')
        self.assertTrue(preparation['success'])
        
        # 5. Cleanup
        engine.cleanup()


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestVerificationEngine))
    suite.addTest(unittest.makeSuite(TestVerificationBatch))
    suite.addTest(unittest.makeSuite(TestVerificationEngineIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)