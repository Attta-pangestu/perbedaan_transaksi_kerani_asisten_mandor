"""
Database Connection Manager untuk FFB Template System
Menggunakan SQLAlchemy dengan Firebird driver
"""

import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

Base = declarative_base()

class FirebirdConnectionManager:
    """
    Manager untuk koneksi database Firebird dengan SQLAlchemy
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connection manager

        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize SQLAlchemy engine dengan Firebird"""
        try:
            # Build connection string
            db_path = self.config.get('database_path')
            username = self.config.get('username', 'sysdba')
            password = self.config.get('password', 'masterkey')

            if not db_path:
                raise ValueError("Database path is required")

            # Firebird connection string dengan fdb driver
            connection_string = f"firebird+fdb://{username}:{password}@{db_path}"

            # Create engine dengan konfigurasi untuk Firebird
            self.engine = create_engine(
                connection_string,
                poolclass=StaticPool,
                pool_pre_ping=True,
                echo=self.config.get('echo', False),
                connect_args={
                    "charset": "UTF8"
                }
            )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Add event listeners untuk optimasi Firebird
            self._add_firebird_listeners()

            logger.info(f"Connected to Firebird database: {db_path}")

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _add_firebird_listeners(self):
        """Add SQLAlchemy event listeners untuk Firebird optimization"""

        @event.listens_for(self.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Optimize queries untuk Firebird"""
            # Log query execution
            if self.config.get('log_queries', False):
                logger.debug(f"Executing: {statement}")
                logger.debug(f"Parameters: {parameters}")

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Setup connection parameters untuk Firebird"""
            # Set connection timeout
            try:
                dbapi_connection.execute(text("SET TRANSACTION WAIT"))
            except Exception:
                pass  # Ignore jika tidak supported

    def get_session(self) -> Session:
        """
        Get database session

        Returns:
            SQLAlchemy Session instance
        """
        return self.SessionLocal()

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful
        """
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1 FROM RDB$DATABASE"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def create_tables(self):
        """Create all database tables from SQLAlchemy models"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information

        Returns:
            Database information dictionary
        """
        try:
            with self.get_session() as session:
                # Get Firebird version
                version_result = session.execute(text(
                    "SELECT RDB$GET_CONTEXT('SYSTEM', 'ENGINE_VERSION') as version FROM RDB$DATABASE"
                ))
                version = version_result.fetchone()[0] if version_result.fetchone() else "Unknown"

                # Get table count
                table_result = session.execute(text(
                    "SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0"
                ))
                table_count = table_result.fetchone()[0]

                return {
                    "version": version,
                    "table_count": table_count,
                    "connection_string": self.engine.url,
                    "dialect": self.engine.dialect.name
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}


class MultiEstateConnectionManager:
    """
    Manager untuk multi-estate database connections
    """

    def __init__(self, estate_configs: Dict[str, Dict[str, Any]]):
        """
        Initialize multi-estate connection manager

        Args:
            estate_configs: Dictionary dengan konfigurasi per estate
        """
        self.estate_configs = estate_configs
        self.connections: Dict[str, FirebirdConnectionManager] = {}
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize connections untuk semua estates"""
        for estate_name, config in self.estate_configs.items():
            try:
                self.connections[estate_name] = FirebirdConnectionManager(config)
                logger.info(f"Connected to estate: {estate_name}")
            except Exception as e:
                logger.error(f"Failed to connect to estate {estate_name}: {e}")

    def get_connection(self, estate_name: str) -> Optional[FirebirdConnectionManager]:
        """
        Get connection untuk estate tertentu

        Args:
            estate_name: Nama estate

        Returns:
            FirebirdConnectionManager instance atau None
        """
        return self.connections.get(estate_name)

    def test_all_connections(self) -> Dict[str, bool]:
        """
        Test semua estate connections

        Returns:
            Dictionary dengan test results per estate
        """
        results = {}
        for estate_name, connection in self.connections.items():
            results[estate_name] = connection.test_connection()
        return results

    def get_available_estates(self) -> list:
        """
        Get list estate yang available

        Returns:
            List estate names
        """
        return list(self.connections.keys())

    def get_session(self, estate_name: str) -> Optional[Session]:
        """
        Get session untuk estate tertentu

        Args:
            estate_name: Nama estate

        Returns:
            SQLAlchemy Session instance atau None
        """
        connection = self.get_connection(estate_name)
        if connection:
            return connection.get_session()
        return None


# Connection factory function
def create_connection_manager(config: Dict[str, Any]) -> FirebirdConnectionManager:
    """
    Factory function untuk create connection manager

    Args:
        config: Database configuration

    Returns:
        FirebirdConnectionManager instance
    """
    return FirebirdConnectionManager(config)


def create_multi_estate_manager(config_path: str) -> MultiEstateConnectionManager:
    """
    Factory function untuk create multi-estate manager

    Args:
        config_path: Path ke konfigurasi estate JSON file

    Returns:
        MultiEstateConnectionManager instance
    """
    import json

    with open(config_path, 'r') as f:
        estate_configs = json.load(f)

    # Convert config ke format yang dibutuhkan
    formatted_configs = {}
    for estate_name, db_path in estate_configs.items():
        formatted_configs[estate_name] = {
            'database_path': db_path,
            'username': 'sysdba',
            'password': 'masterkey',
            'echo': False
        }

    return MultiEstateConnectionManager(formatted_configs)


# Dependency untuk Flask app
def get_database_session() -> Session:
    """
    Dependency untuk get database session dalam Flask context

    Returns:
        Database session
    """
    # Ini akan diimplementasikan dalam Flask app context
    pass