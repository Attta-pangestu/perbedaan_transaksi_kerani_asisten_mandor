#!/usr/bin/env python3
"""
Core Database Module for FFB Analysis System
Handles all Firebird database operations and connection management.
"""

import os
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date

from ..utils.firebird_connector import FirebirdConnector


class DatabaseManager:
    """
    Manages database connections and operations for FFB analysis system.
    Provides unified interface for multi-estate database access.
    """

    def __init__(self, config: Dict[str, str]):
        """
        Initialize database manager with estate configurations.

        Args:
            config: Dictionary mapping estate names to database paths
        """
        self.config = config
        self.connections = {}
        self.employee_cache = {}

    def get_connection(self, estate_name: str) -> Optional[FirebirdConnector]:
        """
        Get database connection for specified estate.

        Args:
            estate_name: Name of the estate

        Returns:
            FirebirdConnector instance or None if connection fails
        """
        if estate_name not in self.config:
            print(f"Estate {estate_name} not found in configuration")
            return None

        if estate_name not in self.connections:
            db_path = self.config[estate_name]

            # Handle folder paths (like PGE 2A)
            if os.path.isdir(db_path):
                db_path = self._find_fdb_in_folder(db_path)

            if not os.path.exists(db_path):
                print(f"Database file not found: {db_path}")
                return None

            try:
                connector = FirebirdConnector(db_path)
                if connector.test_connection():
                    self.connections[estate_name] = connector
                else:
                    print(f"Failed to connect to {estate_name} database")
                    return None
            except Exception as e:
                print(f"Error connecting to {estate_name}: {e}")
                return None

        return self.connections.get(estate_name)

    def _find_fdb_in_folder(self, folder_path: str) -> Optional[str]:
        """Find .FDB file in the specified folder."""
        for file in os.listdir(folder_path):
            if file.upper().endswith('.FDB'):
                return os.path.join(folder_path, file)
        return None

    def get_employee_mapping(self, estate_name: str) -> Dict[str, str]:
        """
        Get employee ID to name mapping for estate.

        Args:
            estate_name: Name of the estate

        Returns:
            Dictionary mapping employee IDs to names
        """
        if estate_name in self.employee_cache:
            return self.employee_cache[estate_name]

        connector = self.get_connection(estate_name)
        if not connector:
            return {}

        try:
            result = connector.execute_query("SELECT ID, NAME FROM EMP")
            df = connector.to_pandas(result)

            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    emp_id = str(row.iloc[0]).strip()
                    emp_name = str(row.iloc[1]).strip()
                    mapping[emp_id] = emp_name

            self.employee_cache[estate_name] = mapping
            return mapping

        except Exception as e:
            print(f"Error getting employee mapping for {estate_name}: {e}")
            return {}

    def get_divisions(self, estate_name: str, start_date: date, end_date: date) -> Tuple[Dict[str, str], List[str]]:
        """
        Get divisions and corresponding monthly tables for the date range.

        Args:
            estate_name: Name of the estate
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Tuple of (divisions_dict, month_tables_list)
        """
        connector = self.get_connection(estate_name)
        if not connector:
            return {}, []

        # Generate month tables within date range
        month_tables = self._generate_month_tables(start_date, end_date)

        all_divisions = {}
        for ffb_table in month_tables:
            try:
                query = f"""
                SELECT DISTINCT b.DIVID, c.DIVNAME
                FROM {ffb_table} a
                JOIN OCFIELD b ON a.FIELDID = b.ID
                LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
                WHERE b.DIVID IS NOT NULL AND c.DIVNAME IS NOT NULL
                """

                result = connector.execute_query(query)
                df = connector.to_pandas(result)

                if not df.empty:
                    for _, row in df.iterrows():
                        div_id = str(row.iloc[0]).strip()
                        div_name = str(row.iloc[1]).strip()
                        if div_id not in all_divisions:
                            all_divisions[div_id] = div_name

            except Exception as e:
                print(f"Warning: Error getting divisions from {ffb_table}: {e}")
                continue

        return all_divisions, month_tables

    def _generate_month_tables(self, start_date: date, end_date: date) -> List[str]:
        """Generate list of month tables within date range."""
        month_tables = []
        current_date = start_date

        while current_date <= end_date:
            month_tables.append(f"FFBSCANNERDATA{current_date.month:02d}")
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)

        return list(set(month_tables))  # Remove duplicates

    def get_transaction_data(self, estate_name: str, div_id: str, start_date: date, end_date: date, month_tables: List[str]) -> pd.DataFrame:
        """
        Get transaction data for specific division and date range.

        Args:
            estate_name: Name of the estate
            div_id: Division ID
            start_date: Start date
            end_date: End date
            month_tables: List of monthly tables to query

        Returns:
            DataFrame with transaction data
        """
        connector = self.get_connection(estate_name)
        if not connector:
            return pd.DataFrame()

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        all_data_df = pd.DataFrame()

        for ffb_table in month_tables:
            try:
                query = f"""
                SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
                       a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
                       a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
                       a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
                       a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
                FROM {ffb_table} a
                JOIN OCFIELD b ON a.FIELDID = b.ID
                WHERE b.DIVID = '{div_id}'
                    AND a.TRANSDATE >= '{start_str}'
                    AND a.TRANSDATE <= '{end_str}'
                """

                result = connector.execute_query(query)
                df_monthly = connector.to_pandas(result)

                if not df_monthly.empty:
                    all_data_df = pd.concat([all_data_df, df_monthly], ignore_index=True)

            except Exception as e:
                print(f"Warning: Error getting data from {ffb_table}: {e}")
                continue

        if not all_data_df.empty:
            # Remove duplicates if there's overlapping data
            all_data_df.drop_duplicates(subset=['ID'], inplace=True)

        return all_data_df

    def test_all_connections(self) -> Dict[str, bool]:
        """
        Test connections to all configured estates.

        Returns:
            Dictionary mapping estate names to connection status
        """
        results = {}
        for estate_name in self.config:
            connector = self.get_connection(estate_name)
            results[estate_name] = connector is not None

        return results

    def close_all_connections(self):
        """Close all active database connections."""
        for estate_name, connector in self.connections.items():
            try:
                # FirebirdConnector doesn't have explicit close method
                # Connections are closed automatically when objects are destroyed
                pass
            except Exception as e:
                print(f"Error closing connection for {estate_name}: {e}")

        self.connections.clear()
        self.employee_cache.clear()


class EstateConfig:
    """
    Manages estate configuration and path validation.
    """

    DEFAULT_CONFIG = {
        "PGE 1A": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1a/PTRJ_P1A.FDB",
        "PGE 1B": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1b/PTRJ_P1B.FDB",
        "PGE 2A": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_PGE_2A_24-10-2025/PTRJ_P2A.FDB",
        "PGE 2B": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_2B_24-10-2025/PTRJ_P2B.FDB",
        "IJL": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_IJL_24-10-2025/PTRJ_IJL_IMPIANJAYALESTARI.FDB",
        "DME": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/dme/PTRJ_DME.FDB",
        "Are B2": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_ARE_B2_24-10-2025/PTRJ_AB2.FDB",
        "Are B1": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_ARE_B1_24-10-2025/PTRJ_AB1.FDB",
        "Are A": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_ARE_A_24-10-2025/PTRJ_ARA.FDB",
        "Are C": r"D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_ARE_C_24-10-2025/PTRJ_ARC.FDB"
    }

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize estate configuration.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.estates = self._load_config()

    def _load_config(self) -> Dict[str, str]:
        """Load configuration from file or use defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    import json
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Error loading config file {self.config_file}: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config_data: Dict[str, str] = None):
        """
        Save configuration to file.

        Args:
            config_data: Configuration data to save (uses current if None)
        """
        if config_data is None:
            config_data = self.estates

        try:
            with open(self.config_file, 'w') as f:
                import json
                json.dump(config_data, f, indent=4)
            print(f"Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Error saving configuration: {e}")

    def validate_paths(self) -> Dict[str, bool]:
        """
        Validate all database paths.

        Returns:
            Dictionary mapping estate names to path validation status
        """
        validation_results = {}
        for estate_name, db_path in self.estates.items():
            # Handle folder paths
            if os.path.isdir(db_path):
                db_path = self._find_fdb_in_folder(db_path)

            validation_results[estate_name] = os.path.exists(db_path)

        return validation_results

    def _find_fdb_in_folder(self, folder_path: str) -> Optional[str]:
        """Find .FDB file in the specified folder."""
        for file in os.listdir(folder_path):
            if file.upper().endswith('.FDB'):
                return os.path.join(folder_path, file)
        return None

    def update_estate_path(self, estate_name: str, new_path: str):
        """
        Update database path for specific estate.

        Args:
            estate_name: Name of the estate
            new_path: New database path
        """
        self.estates[estate_name] = new_path

    def get_estate_names(self) -> List[str]:
        """Get list of all configured estate names."""
        return list(self.estates.keys())