"""
Logging Configuration
Sistem logging komprehensif untuk verification template system.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
import traceback

from ..config.settings import Settings


class VerificationLogger:
    """
    Logger khusus untuk sistem verifikasi dengan fitur advanced.
    """
    
    def __init__(self, 
                 name: str = "verification_system",
                 log_level: Union[str, int] = logging.INFO,
                 enable_file_logging: bool = True,
                 enable_console_logging: bool = True):
        """
        Initialize verification logger.
        
        Args:
            name: Nama logger
            log_level: Level logging
            enable_file_logging: Enable logging ke file
            enable_console_logging: Enable logging ke console
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.settings = Settings()
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self.logger.setLevel(log_level)
        
        # Setup handlers
        if enable_console_logging:
            self._setup_console_handler()
        
        if enable_file_logging:
            self._setup_file_handlers()
        
        # Setup custom formatters
        self._setup_formatters()
        
        # Verification session tracking
        self.session_id = None
        self.session_start_time = None
        self.session_logs = []
    
    def _setup_console_handler(self):
        """
        Setup console handler dengan format yang user-friendly.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Format sederhana untuk console
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self):
        """
        Setup file handlers untuk berbagai level logging.
        """
        # Pastikan direktori log ada
        log_dir = self.settings.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Main log file (semua level)
        main_log_file = log_dir / f"{self.name}.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        
        # Error log file (error dan critical saja)
        error_log_file = log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # Verification log file (khusus untuk proses verifikasi)
        verification_log_file = log_dir / f"{self.name}_verification.log"
        verification_handler = logging.handlers.RotatingFileHandler(
            verification_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10,
            encoding='utf-8'
        )
        verification_handler.setLevel(logging.INFO)
        
        # Add handlers
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(verification_handler)
        
        # Store handlers untuk reference
        self.main_handler = main_handler
        self.error_handler = error_handler
        self.verification_handler = verification_handler
    
    def _setup_formatters(self):
        """
        Setup custom formatters untuk berbagai handler.
        """
        # Detailed formatter untuk file logging
        detailed_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # JSON formatter untuk structured logging
        json_format = JsonFormatter()
        
        # Apply formatters
        if hasattr(self, 'main_handler'):
            self.main_handler.setFormatter(detailed_format)
        
        if hasattr(self, 'error_handler'):
            self.error_handler.setFormatter(detailed_format)
        
        if hasattr(self, 'verification_handler'):
            self.verification_handler.setFormatter(detailed_format)
    
    def start_verification_session(self, session_info: Dict[str, Any]):
        """
        Mulai session verifikasi dengan tracking khusus.
        
        Args:
            session_info: Informasi session (template, estate, dll)
        """
        self.session_id = f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start_time = datetime.now()
        self.session_logs = []
        
        session_data = {
            'session_id': self.session_id,
            'start_time': self.session_start_time.isoformat(),
            'session_info': session_info
        }
        
        self.logger.info(f"=== VERIFICATION SESSION STARTED ===")
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Template: {session_info.get('template_name', 'N/A')}")
        self.logger.info(f"Estate: {session_info.get('estate_name', 'N/A')}")
        self.logger.info(f"Date Range: {session_info.get('start_date', 'N/A')} - {session_info.get('end_date', 'N/A')}")
        
        # Log ke file session khusus
        self._log_session_data(session_data, 'session_start')
    
    def end_verification_session(self, session_result: Dict[str, Any]):
        """
        Akhiri session verifikasi dengan summary.
        
        Args:
            session_result: Hasil session
        """
        if not self.session_id:
            self.logger.warning("No active verification session to end")
            return
        
        end_time = datetime.now()
        duration = (end_time - self.session_start_time).total_seconds()
        
        session_summary = {
            'session_id': self.session_id,
            'start_time': self.session_start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'result': session_result,
            'total_logs': len(self.session_logs)
        }
        
        self.logger.info(f"=== VERIFICATION SESSION ENDED ===")
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Success: {session_result.get('success', False)}")
        
        if not session_result.get('success', False):
            self.logger.error(f"Session failed: {session_result.get('error', 'Unknown error')}")
        
        # Log ke file session khusus
        self._log_session_data(session_summary, 'session_end')
        
        # Reset session
        self.session_id = None
        self.session_start_time = None
        self.session_logs = []
    
    def _log_session_data(self, data: Dict[str, Any], event_type: str):
        """
        Log data session ke file khusus.
        
        Args:
            data: Data untuk di-log
            event_type: Tipe event
        """
        try:
            session_log_file = self.settings.LOGS_DIR / "verification_sessions.jsonl"
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data
            }
            
            with open(session_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log session data: {e}")
    
    def log_verification_step(self, step_name: str, step_data: Dict[str, Any], level: int = logging.INFO):
        """
        Log step dalam proses verifikasi.
        
        Args:
            step_name: Nama step
            step_data: Data step
            level: Level logging
        """
        step_info = {
            'step_name': step_name,
            'step_data': step_data,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.session_id:
            step_info['session_id'] = self.session_id
            self.session_logs.append(step_info)
        
        message = f"STEP: {step_name}"
        if 'message' in step_data:
            message += f" - {step_data['message']}"
        
        self.logger.log(level, message)
        
        # Log detail ke file jika ada
        if len(step_data) > 1 or 'message' not in step_data:
            self.logger.debug(f"Step details: {json.dumps(step_data, ensure_ascii=False, default=str)}")
    
    def log_database_operation(self, operation: str, query: str, params: Optional[Dict] = None, 
                             result_count: Optional[int] = None, duration: Optional[float] = None):
        """
        Log operasi database.
        
        Args:
            operation: Jenis operasi (SELECT, INSERT, dll)
            query: Query SQL
            params: Parameter query
            result_count: Jumlah hasil
            duration: Durasi eksekusi
        """
        db_info = {
            'operation': operation,
            'query': query[:200] + '...' if len(query) > 200 else query,  # Truncate long queries
            'params': params,
            'result_count': result_count,
            'duration_seconds': duration
        }
        
        message = f"DB {operation}"
        if result_count is not None:
            message += f" - {result_count} rows"
        if duration is not None:
            message += f" - {duration:.3f}s"
        
        self.logger.info(message)
        self.logger.debug(f"DB operation details: {json.dumps(db_info, ensure_ascii=False, default=str)}")
    
    def log_template_operation(self, template_name: str, operation: str, details: Dict[str, Any]):
        """
        Log operasi template.
        
        Args:
            template_name: Nama template
            operation: Jenis operasi
            details: Detail operasi
        """
        template_info = {
            'template_name': template_name,
            'operation': operation,
            'details': details
        }
        
        message = f"TEMPLATE {template_name}: {operation}"
        self.logger.info(message)
        self.logger.debug(f"Template operation: {json.dumps(template_info, ensure_ascii=False, default=str)}")
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """
        Log error dengan context lengkap.
        
        Args:
            error: Exception yang terjadi
            context: Context saat error terjadi
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_traceback': traceback.format_exc(),
            'context': context,
            'session_id': self.session_id
        }
        
        self.logger.error(f"ERROR: {type(error).__name__}: {str(error)}")
        self.logger.error(f"Context: {json.dumps(context, ensure_ascii=False, default=str)}")
        self.logger.debug(f"Full error info: {json.dumps(error_info, ensure_ascii=False, default=str)}")
    
    def get_session_logs(self) -> List[Dict[str, Any]]:
        """
        Dapatkan log session saat ini.
        
        Returns:
            List: Log session
        """
        return self.session_logs.copy()
    
    def export_session_logs(self, output_path: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Export log session ke file.
        
        Args:
            output_path: Path output
        
        Returns:
            str: Path file yang di-export
        """
        if not self.session_logs:
            self.logger.warning("No session logs to export")
            return None
        
        try:
            if output_path:
                export_file = Path(output_path)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"session_logs_{self.session_id or timestamp}.json"
                export_file = self.settings.LOGS_DIR / filename
            
            export_data = {
                'session_id': self.session_id,
                'export_time': datetime.now().isoformat(),
                'total_logs': len(self.session_logs),
                'logs': self.session_logs
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Session logs exported to: {export_file}")
            return str(export_file)
            
        except Exception as e:
            self.logger.error(f"Failed to export session logs: {e}")
            return None


class JsonFormatter(logging.Formatter):
    """
    Custom formatter untuk output JSON.
    """
    
    def format(self, record):
        """
        Format log record sebagai JSON.
        
        Args:
            record: Log record
        
        Returns:
            str: JSON formatted log
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Tambahkan exception info jika ada
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Tambahkan extra fields jika ada
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                          'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_logging(log_level: Union[str, int] = logging.INFO,
                 enable_file_logging: bool = True,
                 enable_console_logging: bool = True) -> VerificationLogger:
    """
    Setup logging untuk aplikasi.
    
    Args:
        log_level: Level logging
        enable_file_logging: Enable file logging
        enable_console_logging: Enable console logging
    
    Returns:
        VerificationLogger: Instance logger
    """
    return VerificationLogger(
        name="verification_system",
        log_level=log_level,
        enable_file_logging=enable_file_logging,
        enable_console_logging=enable_console_logging
    )


def get_logger(name: str) -> logging.Logger:
    """
    Dapatkan logger dengan nama tertentu.
    
    Args:
        name: Nama logger
    
    Returns:
        Logger: Instance logger
    """
    return logging.getLogger(name)


if __name__ == "__main__":
    # Test logging system
    print("=== Logging System Test ===")
    
    try:
        # Setup logger
        logger = setup_logging(log_level=logging.DEBUG)
        
        # Test basic logging
        logger.logger.info("Testing basic logging")
        logger.logger.debug("Debug message")
        logger.logger.warning("Warning message")
        logger.logger.error("Error message")
        
        # Test verification session
        session_info = {
            'template_name': 'transaction_verification',
            'estate_name': 'TEST_ESTATE',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        logger.start_verification_session(session_info)
        
        # Test step logging
        logger.log_verification_step("database_connection", {
            'message': 'Connecting to database',
            'database_path': '/path/to/database.fdb'
        })
        
        logger.log_verification_step("data_retrieval", {
            'message': 'Retrieving employee data',
            'employee_count': 150
        })
        
        # Test database operation logging
        logger.log_database_operation(
            operation="SELECT",
            query="SELECT * FROM EMP WHERE ESTATE = ?",
            params={'estate': 'TEST_ESTATE'},
            result_count=150,
            duration=0.245
        )
        
        # Test template operation logging
        logger.log_template_operation(
            template_name="transaction_verification",
            operation="analyze_division",
            details={'division': 'DIV001', 'records_processed': 500}
        )
        
        # Test error logging
        try:
            raise ValueError("Test error for logging")
        except Exception as e:
            logger.log_error_with_context(e, {
                'operation': 'test_operation',
                'parameters': {'test': True}
            })
        
        # End session
        session_result = {
            'success': True,
            'total_divisions': 5,
            'total_employees': 150
        }
        
        logger.end_verification_session(session_result)
        
        # Export session logs
        export_path = logger.export_session_logs()
        if export_path:
            print(f"Session logs exported to: {export_path}")
        
        print("Logging system test completed!")
        
    except Exception as e:
        print(f"Logging system test failed: {e}")
        raise