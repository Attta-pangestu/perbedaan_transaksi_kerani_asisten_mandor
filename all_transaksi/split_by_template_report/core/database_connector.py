#!/usr/bin/env python3
"""
Modular Database Connector for FFB Analysis System
Provides abstracted database connectivity for template-based reporting
"""

import os
import subprocess
import json
import tempfile
import re
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class DatabaseConnectorInterface(ABC):
    """Abstract interface for database connectors"""
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test database connection"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a database query"""
        pass
    
    @abstractmethod
    def to_pandas(self, result_data: Any) -> pd.DataFrame:
        """Convert query result to pandas DataFrame"""
        pass
    
    @abstractmethod
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        pass


class FirebirdModularConnector(DatabaseConnectorInterface):
    """
    Modular Firebird database connector using isql
    Enhanced version of the original FirebirdConnector with better modularity
    """
    
    def __init__(self, db_path: Optional[str] = None, username: str = 'sysdba', 
                 password: str = 'masterkey', isql_path: Optional[str] = None, 
                 use_localhost: bool = True):
        """
        Initialize Firebird connection
        
        Args:
            db_path: Full path to .fdb file
            username: Database username (default: sysdba)
            password: Database password (default: masterkey)
            isql_path: Path to isql.exe executable (default: auto-detect)
            use_localhost: If True, use localhost:path format for connection (default: True)
        """
        self.db_path = db_path
        self.username = username
        self.password = password
        self.use_localhost = use_localhost
        
        # Auto-detect isql_path if not provided
        if isql_path is None:
            self.isql_path = self._detect_isql_path()
        else:
            self.isql_path = isql_path
        
        # Verify isql exists
        if not os.path.exists(self.isql_path):
            raise FileNotFoundError(f"isql.exe not found at: {self.isql_path}")
    
    def _detect_isql_path(self) -> str:
        """Auto-detect isql.exe location"""
        default_paths = [
            r'C:\Program Files (x86)\Firebird\Firebird_1_5\bin\isql.exe',
            r'C:\Program Files (x86)\Firebird-1.5.6.5026-0_win32_Manual\bin\isql.exe',
            r'C:\Program Files (x86)\Firebird\bin\isql.exe',
            r'C:\Program Files\Firebird\Firebird_2_5\bin\isql.exe',
            r'C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe',
            r'C:\Program Files\Firebird\bin\isql.exe'
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        # If not found in default paths, try to find in PATH
        try:
            result = subprocess.run(['where', 'isql.exe'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        raise FileNotFoundError("isql.exe not found in default locations or PATH")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        if not self.db_path or not os.path.exists(self.db_path):
            return False
        
        try:
            # Simple query to test connection
            result = self.execute_query("SELECT 1 FROM RDB$DATABASE;")
            return result is not None
        except Exception:
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Execute SQL query using isql
        
        Args:
            query: SQL query string
            params: Query parameters (not implemented for isql)
            
        Returns:
            List of dictionaries representing query results
        """
        if not self.db_path:
            raise ValueError("Database path not set")
        
        try:
            # Prepare connection string and SQL command
            if self.use_localhost:
                connection_string = f"localhost:'{self.db_path}'"
                connect_command = f"CONNECT {connection_string} USER '{self.username}' PASSWORD '{self.password}';\n"
            else:
                connection_string = self.db_path
                connect_command = f"CONNECT '{connection_string}' USER '{self.username}' PASSWORD '{self.password}';\n"
            
            # Write SQL with explicit CONNECT statement
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                temp_file.write(connect_command)
                temp_file.write(query)
                temp_file.write('\nEXIT;\n')
                temp_sql_path = temp_file.name
            
            # Execute isql command
            cmd = [
                self.isql_path,
                '-input', temp_sql_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode != 0:
                raise Exception(f"Query execution failed: {result.stderr}")
            
            # Parse output
            return self._parse_isql_output(result.stdout)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_sql_path)
            except:
                pass
    
    def _parse_isql_output(self, output_text: str) -> List[Dict]:
        """Parse isql output into structured data"""
        lines = output_text.strip().split('\n')
        
        # Find data section (skip headers and separators)
        data_start = -1
        headers = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for column headers (usually after "SQL>" prompt)
            if 'SQL>' in line:
                continue
            
            # Skip separator lines (contain only = or -)
            if re.match(r'^[=\-\s]+$', line):
                continue
            
            # First non-empty, non-separator line after SQL> is likely headers
            if not headers and not re.match(r'^[=\-\s]+$', line):
                # Extract column names
                headers = [col.strip() for col in re.split(r'\s{2,}', line) if col.strip()]
                data_start = i + 1
                break
        
        if not headers or data_start == -1:
            return []
        
        # Parse data rows
        results = []
        for i in range(data_start, len(lines)):
            line = lines[i].strip()
            
            # Skip empty lines and separators
            if not line or re.match(r'^[=\-\s]+$', line):
                continue
            
            # Stop at SQL> prompt or other control lines
            if 'SQL>' in line or line.startswith('Records affected:'):
                break
            
            # Split data by multiple spaces (similar to headers)
            values = [val.strip() for val in re.split(r'\s{2,}', line)]
            
            # Create row dictionary
            if len(values) >= len(headers):
                row = {}
                for j, header in enumerate(headers):
                    if j < len(values):
                        row[header] = values[j] if values[j] != '<null>' else None
                    else:
                        row[header] = None
                results.append(row)
        
        return results
    
    def to_pandas(self, result_data: Optional[List[Dict]]) -> pd.DataFrame:
        """Convert query result to pandas DataFrame"""
        if not result_data:
            return pd.DataFrame()
        
        return pd.DataFrame(result_data)
    
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        query = """
        SELECT RDB$RELATION_NAME 
        FROM RDB$RELATIONS 
        WHERE RDB$SYSTEM_FLAG = 0 
        ORDER BY RDB$RELATION_NAME;
        """
        
        try:
            result = self.execute_query(query)
            if result:
                return [row['RDB$RELATION_NAME'].strip() for row in result]
            return []
        except Exception:
            return []
    
    def get_employee_mapping(self) -> Dict[str, str]:
        """Get employee ID to name mapping"""
        query = "SELECT ID, NAME FROM EMP"
        try:
            result = self.execute_query(query)
            if result:
                return {str(row['ID']).strip(): str(row['NAME']).strip() 
                       for row in result if row['ID'] and row['NAME']}
            return {}
        except Exception:
            return {}
    
    def get_division_list(self) -> List[Dict[str, str]]:
        """Get division list from FFBScanner table"""
        query = """
        SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
        FROM FFBSCANNERDATA04 a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        WHERE b.DIVID IS NOT NULL
        ORDER BY c.DIVNAME
        """
        
        try:
            result = self.execute_query(query)
            divisions = []
            if result:
                for row in result:
                    div_id = str(row['DIVID']).strip() if row['DIVID'] else ''
                    div_name = str(row['DIVNAME']).strip() if row['DIVNAME'] else ''
                    
                    if div_id and div_name:
                        divisions.append({
                            'div_id': div_id,
                            'div_name': div_name
                        })
            
            return divisions
        except Exception:
            return []


class DatabaseConnectorFactory:
    """Factory for creating database connectors"""
    
    @staticmethod
    def create_connector(connector_type: str = 'firebird', **kwargs) -> DatabaseConnectorInterface:
        """
        Create database connector instance
        
        Args:
            connector_type: Type of connector ('firebird')
            **kwargs: Connector-specific arguments
            
        Returns:
            Database connector instance
        """
        if connector_type.lower() == 'firebird':
            return FirebirdModularConnector(**kwargs)
        else:
            raise ValueError(f"Unsupported connector type: {connector_type}")


# Configuration class for database settings
class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize database configuration
        
        Args:
            config_file: Path to configuration file (JSON format)
        """
        self.config = {}
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config file: {e}")
    
    def get_db_config(self, profile: str = 'default') -> Dict[str, Any]:
        """Get database configuration for specific profile"""
        return self.config.get('database', {}).get(profile, {})
    
    def set_db_config(self, profile: str, config: Dict[str, Any]) -> None:
        """Set database configuration for specific profile"""
        if 'database' not in self.config:
            self.config['database'] = {}
        self.config['database'][profile] = config
    
    def save_to_file(self, config_file: str) -> None:
        """Save configuration to JSON file"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save config file: {e}")