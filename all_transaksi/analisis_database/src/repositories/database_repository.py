"""
Database Repository
Base repository class for database operations
"""

from typing import Dict, Any, List, Optional
from infrastructure.database.firebird_connector import FirebirdConnector, ConnectionFactory


class DatabaseRepository:
    """
    Base repository class for database operations
    """

    def __init__(self, connector: FirebirdConnector):
        """
        Initialize repository with database connector

        :param connector: FirebirdConnector instance
        """
        self.connector = connector

    @classmethod
    def create(cls, db_path: str, username: str = 'sysdba',
               password: str = 'masterkey', use_localhost: bool = False) -> 'DatabaseRepository':
        """
        Create repository with new database connection

        :param db_path: Database file path
        :param username: Database username
        :param password: Database password
        :param use_localhost: Whether to use localhost format
        :return: DatabaseRepository instance
        """
        connector = ConnectionFactory.create_connection(
            db_path=db_path,
            username=username,
            password=password,
            use_localhost=use_localhost
        )
        return cls(connector)

    def test_connection(self) -> bool:
        """
        Test database connection

        :return: True if connection successful
        """
        return self.connector.test_connection()

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute SQL query

        :param query: SQL query string
        :param params: Query parameters (not used in current implementation)
        :return: Query results as list of dictionaries
        """
        try:
            result = self.connector.execute_query(query, params, as_dict=True)
            if result and result[0].get("rows"):
                return result[0]["rows"]
            return []
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    def get_tables(self) -> List[str]:
        """
        Get list of tables in database

        :return: List of table names
        """
        try:
            return self.connector.get_tables()
        except Exception as e:
            print(f"Error getting tables: {e}")
            return []

    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists in database

        :param table_name: Table name to check
        :return: True if table exists
        """
        tables = self.get_tables()
        return table_name.upper() in [t.upper() for t in tables]

    def get_table_count(self, table_name: str) -> int:
        """
        Get number of records in table

        :param table_name: Table name
        :return: Number of records
        """
        if not self.table_exists(table_name):
            return 0

        query = f"SELECT COUNT(*) as TOTAL FROM {table_name}"
        try:
            result = self.execute_query(query)
            if result:
                return int(result[0].get('TOTAL', 0))
        except Exception as e:
            print(f"Error getting table count for {table_name}: {e}")
        return 0

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a table

        :param table_name: Table name
        :return: Dictionary with table information
        """
        return {
            'name': table_name,
            'exists': self.table_exists(table_name),
            'record_count': self.get_table_count(table_name)
        }

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database

        :return: Dictionary with database information
        """
        tables = self.get_tables()
        table_info = {}

        # Get info for main transaction tables
        transaction_tables = [f"FFBSCANNERDATA{i:02d}" for i in range(1, 13)]
        for table in transaction_tables:
            table_info[table] = self.get_table_info(table)

        return {
            'database_path': self.connector.db_path,
            'connection_status': self.test_connection(),
            'total_tables': len(tables),
            'tables': tables,
            'transaction_tables': table_info
        }

    def validate_database_structure(self) -> Dict[str, Any]:
        """
        Validate that database has required structure

        :return: Dictionary with validation results
        """
        validation_result = {
            'is_valid': True,
            'missing_tables': [],
            'empty_tables': [],
            'errors': []
        }

        # Check required tables
        required_tables = ['EMP', 'OCFIELD', 'CRDIVISION']
        for table in required_tables:
            if not self.table_exists(table):
                validation_result['missing_tables'].append(table)
                validation_result['is_valid'] = False

        # Check for at least one transaction table
        has_transaction_data = False
        for i in range(1, 13):
            table_name = f"FFBSCANNERDATA{i:02d}"
            if self.table_exists(table_name):
                count = self.get_table_count(table_name)
                if count > 0:
                    has_transaction_data = True
                else:
                    validation_result['empty_tables'].append(table_name)

        if not has_transaction_data:
            validation_result['is_valid'] = False
            validation_result['errors'].append("No transaction data found in any monthly table")

        return validation_result

    def close(self):
        """Close database connection (placeholder for future implementation)"""
        # FirebirdConnector doesn't have explicit close method in current implementation
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()