#!/usr/bin/env python3
"""
Unit tests for logging configuration module.
"""

import unittest
import tempfile
import json
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from verification_template_system.core.logging_config import (
    VerificationLogger, JsonFormatter, setup_logging, get_logger
)


class TestJsonFormatter(unittest.TestCase):
    """Test cases for JsonFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JsonFormatter()
    
    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/path/to/file.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed['level'], 'INFO')
        self.assertEqual(parsed['message'], 'Test message')
        self.assertEqual(parsed['logger'], 'test_logger')
        self.assertEqual(parsed['filename'], 'file.py')
        self.assertEqual(parsed['lineno'], 42)
        self.assertIn('timestamp', parsed)
    
    def test_format_record_with_extra_fields(self):
        """Test formatting a log record with extra fields."""
        record = logging.LogRecord(
            name='test_logger',
            level=logging.ERROR,
            pathname='/path/to/file.py',
            lineno=42,
            msg='Error occurred',
            args=(),
            exc_info=None
        )
        
        # Add extra fields
        record.template_name = 'test_template'
        record.estate_name = 'Test Estate'
        record.verification_id = 'ver_123'
        
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed['template_name'], 'test_template')
        self.assertEqual(parsed['estate_name'], 'Test Estate')
        self.assertEqual(parsed['verification_id'], 'ver_123')
    
    def test_format_record_with_exception(self):
        """Test formatting a log record with exception info."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name='test_logger',
            level=logging.ERROR,
            pathname='/path/to/file.py',
            lineno=42,
            msg='Exception occurred',
            args=(),
            exc_info=exc_info
        )
        
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertIn('exception', parsed)
        self.assertIn('ValueError', parsed['exception'])
        self.assertIn('Test exception', parsed['exception'])


class TestVerificationLogger(unittest.TestCase):
    """Test cases for VerificationLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.logs_dir)
        
        self.logger = VerificationLogger(
            name="test_verification",
            log_dir=self.logs_dir,
            console_level=logging.DEBUG,
            file_level=logging.INFO
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Close all handlers
        for handler in self.logger.logger.handlers[:]:
            handler.close()
            self.logger.logger.removeHandler(handler)
        
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test VerificationLogger initialization."""
        self.assertEqual(self.logger.name, "test_verification")
        self.assertEqual(self.logger.log_dir, self.logs_dir)
        self.assertIsNotNone(self.logger.logger)
        
        # Check handlers are created
        handlers = self.logger.logger.handlers
        self.assertGreater(len(handlers), 0)
    
    def test_log_levels(self):
        """Test different log levels."""
        # Test each log level
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        
        # Check that log files are created
        log_files = os.listdir(self.logs_dir)
        self.assertGreater(len(log_files), 0)
    
    def test_start_verification_session(self):
        """Test starting a verification session."""
        session_id = self.logger.start_verification_session(
            template_name="test_template",
            estate_name="Test Estate",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.logger.active_sessions)
        
        session = self.logger.active_sessions[session_id]
        self.assertEqual(session['template_name'], "test_template")
        self.assertEqual(session['estate_name'], "Test Estate")
        self.assertEqual(session['start_date'], "2024-01-01")
        self.assertEqual(session['end_date'], "2024-01-31")
    
    def test_end_verification_session_success(self):
        """Test ending a verification session successfully."""
        session_id = self.logger.start_verification_session(
            template_name="test_template",
            estate_name="Test Estate"
        )
        
        result = self.logger.end_verification_session(
            session_id=session_id,
            success=True,
            results_summary={"total_records": 100}
        )
        
        self.assertTrue(result)
        self.assertNotIn(session_id, self.logger.active_sessions)
    
    def test_end_verification_session_failure(self):
        """Test ending a verification session with failure."""
        session_id = self.logger.start_verification_session(
            template_name="test_template",
            estate_name="Test Estate"
        )
        
        result = self.logger.end_verification_session(
            session_id=session_id,
            success=False,
            error_message="Test error occurred"
        )
        
        self.assertTrue(result)
        self.assertNotIn(session_id, self.logger.active_sessions)
    
    def test_end_nonexistent_session(self):
        """Test ending a non-existent session."""
        result = self.logger.end_verification_session(
            session_id="nonexistent_session",
            success=True
        )
        
        self.assertFalse(result)
    
    def test_log_verification_step(self):
        """Test logging verification steps."""
        session_id = self.logger.start_verification_session(
            template_name="test_template",
            estate_name="Test Estate"
        )
        
        # Log various steps
        self.logger.log_verification_step(
            session_id=session_id,
            step_name="data_extraction",
            status="started"
        )
        
        self.logger.log_verification_step(
            session_id=session_id,
            step_name="data_extraction",
            status="completed",
            details={"records_extracted": 500}
        )
        
        self.logger.log_verification_step(
            session_id=session_id,
            step_name="validation",
            status="failed",
            error="Validation error occurred"
        )
        
        # Verify session tracking
        session = self.logger.active_sessions[session_id]
        self.assertIn('steps', session)
        self.assertGreater(len(session['steps']), 0)
    
    def test_log_database_operation(self):
        """Test logging database operations."""
        self.logger.log_database_operation(
            operation="SELECT",
            table="EMP_TABLE",
            duration=0.5,
            records_affected=100
        )
        
        self.logger.log_database_operation(
            operation="INSERT",
            table="RESULTS_TABLE",
            duration=1.2,
            records_affected=50,
            error="Connection timeout"
        )
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_log_template_operation(self):
        """Test logging template operations."""
        self.logger.log_template_operation(
            operation="load",
            template_name="test_template",
            success=True,
            duration=0.1
        )
        
        self.logger.log_template_operation(
            operation="validate",
            template_name="invalid_template",
            success=False,
            error="Missing required sections"
        )
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_log_error_with_context(self):
        """Test logging errors with context."""
        context = {
            "template_name": "test_template",
            "estate_name": "Test Estate",
            "operation": "data_processing"
        }
        
        self.logger.log_error_with_context(
            error_message="Processing failed",
            context=context,
            exception=ValueError("Test exception")
        )
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_get_session_logs(self):
        """Test getting session logs."""
        session_id = self.logger.start_verification_session(
            template_name="test_template",
            estate_name="Test Estate"
        )
        
        # Log some steps
        self.logger.log_verification_step(session_id, "step1", "completed")
        self.logger.log_verification_step(session_id, "step2", "started")
        
        logs = self.logger.get_session_logs(session_id)
        
        self.assertIsNotNone(logs)
        self.assertIn('session_info', logs)
        self.assertIn('steps', logs)
        self.assertEqual(len(logs['steps']), 2)
    
    def test_get_nonexistent_session_logs(self):
        """Test getting logs for non-existent session."""
        logs = self.logger.get_session_logs("nonexistent_session")
        self.assertIsNone(logs)
    
    def test_cleanup(self):
        """Test logger cleanup."""
        session_id = self.logger.start_verification_session(
            template_name="test_template",
            estate_name="Test Estate"
        )
        
        self.assertEqual(len(self.logger.active_sessions), 1)
        
        self.logger.cleanup()
        
        # Active sessions should be cleared
        self.assertEqual(len(self.logger.active_sessions), 0)


class TestLoggingUtilities(unittest.TestCase):
    """Test cases for logging utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        logger = setup_logging(
            name="test_setup",
            log_dir=self.temp_dir,
            console_level=logging.INFO
        )
        
        self.assertIsInstance(logger, VerificationLogger)
        self.assertEqual(logger.name, "test_setup")
    
    def test_setup_logging_with_config(self):
        """Test logging setup with configuration."""
        config = {
            'console_level': 'DEBUG',
            'file_level': 'WARNING',
            'json_format': True
        }
        
        logger = setup_logging(
            name="test_config",
            log_dir=self.temp_dir,
            **config
        )
        
        self.assertIsInstance(logger, VerificationLogger)
    
    def test_get_logger_new(self):
        """Test getting a new logger."""
        logger = get_logger("new_logger", log_dir=self.temp_dir)
        
        self.assertIsInstance(logger, VerificationLogger)
        self.assertEqual(logger.name, "new_logger")
    
    def test_get_logger_existing(self):
        """Test getting an existing logger."""
        # Create logger first
        logger1 = get_logger("existing_logger", log_dir=self.temp_dir)
        
        # Get the same logger
        logger2 = get_logger("existing_logger")
        
        # Should return the same instance
        self.assertEqual(logger1.name, logger2.name)


class TestLoggingIntegration(unittest.TestCase):
    """Integration tests for logging functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.logs_dir)
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_verification_logging_workflow(self):
        """Test complete verification logging workflow."""
        # Setup logger
        logger = VerificationLogger(
            name="integration_test",
            log_dir=self.logs_dir,
            console_level=logging.INFO,
            file_level=logging.DEBUG
        )
        
        # Start verification session
        session_id = logger.start_verification_session(
            template_name="integration_template",
            estate_name="Integration Estate",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        # Log various operations
        logger.log_template_operation(
            operation="load",
            template_name="integration_template",
            success=True,
            duration=0.2
        )
        
        logger.log_verification_step(
            session_id=session_id,
            step_name="database_connection",
            status="started"
        )
        
        logger.log_database_operation(
            operation="SELECT",
            table="EMP_TABLE",
            duration=1.5,
            records_affected=1000
        )
        
        logger.log_verification_step(
            session_id=session_id,
            step_name="database_connection",
            status="completed",
            details={"connection_time": 1.5}
        )
        
        logger.log_verification_step(
            session_id=session_id,
            step_name="data_processing",
            status="started"
        )
        
        logger.log_verification_step(
            session_id=session_id,
            step_name="data_processing",
            status="completed",
            details={"processed_records": 1000, "verification_rate": 95.5}
        )
        
        # End session successfully
        logger.end_verification_session(
            session_id=session_id,
            success=True,
            results_summary={
                "total_records": 1000,
                "verified_records": 955,
                "verification_rate": 95.5
            }
        )
        
        # Verify log files were created
        log_files = os.listdir(self.logs_dir)
        self.assertGreater(len(log_files), 0)
        
        # Cleanup
        logger.cleanup()
    
    def test_error_handling_workflow(self):
        """Test error handling in logging workflow."""
        logger = VerificationLogger(
            name="error_test",
            log_dir=self.logs_dir
        )
        
        # Start session
        session_id = logger.start_verification_session(
            template_name="error_template",
            estate_name="Error Estate"
        )
        
        # Simulate error scenario
        logger.log_verification_step(
            session_id=session_id,
            step_name="data_extraction",
            status="started"
        )
        
        # Log database error
        logger.log_database_operation(
            operation="SELECT",
            table="NONEXISTENT_TABLE",
            duration=0.1,
            error="Table does not exist"
        )
        
        # Log error with context
        context = {
            "template_name": "error_template",
            "estate_name": "Error Estate",
            "step": "data_extraction"
        }
        
        logger.log_error_with_context(
            error_message="Data extraction failed",
            context=context,
            exception=Exception("Database error")
        )
        
        # End session with failure
        logger.end_verification_session(
            session_id=session_id,
            success=False,
            error_message="Verification failed due to database error"
        )
        
        # Cleanup
        logger.cleanup()


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestJsonFormatter))
    suite.addTest(unittest.makeSuite(TestVerificationLogger))
    suite.addTest(unittest.makeSuite(TestLoggingUtilities))
    suite.addTest(unittest.makeSuite(TestLoggingIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)