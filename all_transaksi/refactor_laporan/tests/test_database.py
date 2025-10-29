"""
Test Suite untuk Database Modules

Test file untuk memvalidasi functionality dari database modules
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.firebird_connector import FirebirdConnector
from database.query_builder import FFBQueryBuilder
from core.config import FFBConfig

class TestFirebirdConnector(unittest.TestCase):
    """
    Test cases untuk FirebirdConnector class
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.test_db_path = "test_database.fdb"
        self.connector = FirebirdConnector(
            db_path=self.test_db_path,
            use_localhost=False
        )

    def test_init(self):
        """
        Test connector initialization
        """
        self.assertEqual(self.connector.db_path, self.test_db_path)
        self.assertEqual(self.connector.username, 'sysdba')
        self.assertEqual(self.connector.password, 'masterkey')
        self.assertFalse(self.connector.use_localhost)

    @patch('os.path.exists')
    def test_isql_path_detection(self, mock_exists):
        """
        Test isql path detection
        """
        # Mock successful path detection
        mock_exists.return_value = True

        with patch.object(self.connector, '_detect_isql_path') as mock_detect:
            mock_detect.return_value = "C:\\test\\isql.exe"
            connector = FirebirdConnector(db_path=self.test_db_path)
            self.assertEqual(connector.isql_path, "C:\\test\\isql.exe")

    def test_query_builder_initialization(self):
        """
        Test query builder initialization
        """
        query_builder = FFBQueryBuilder()
        self.assertEqual(query_builder.table_prefix, "FFBSCANNERDATA")

    def test_monthly_table_name_generation(self):
        """
        Test monthly table name generation
        """
        query_builder = FFBQueryBuilder()

        # Test various months
        self.assertEqual(query_builder.get_monthly_table_name(1), "FFBSCANNERDATA01")
        self.assertEqual(query_builder.get_monthly_table_name(9), "FFBSCANNERDATA09")
        self.assertEqual(query_builder.get_monthly_table_name(12), "FFBSCANNERDATA12")

    def test_base_query_building(self):
        """
        Test base query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        # Test basic query
        query = query_builder.build_base_query(table_name)
        self.assertIn("FROM FFBSCANNERDATA09", query)
        self.assertIn("JOIN OCFIELD", query)
        self.assertIn("LEFT JOIN CRDIVISION", query)

        # Test with date filters
        query = query_builder.build_base_query(
            table_name,
            start_date="2025-09-01",
            end_date="2025-09-30"
        )
        self.assertIn("TRANSDATE >= '2025-09-01'", query)
        self.assertIn("TRANSDATE <= '2025-09-30'", query)

        # Test with estate filter
        query = query_builder.build_base_query(
            table_name,
            estates=["PGE 1A", "PGE 1B"]
        )
        self.assertIn("DIVNAME IN ('PGE 1A', 'PGE 1B')", query)

    def test_kerani_query_building(self):
        """
        Test kerani-specific query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_kerani_transactions_query(table_name)
        self.assertIn("RECORDTAG = 'PM'", query)
        self.assertIn("FROM FFBSCANNERDATA09", query)

    def test_verification_query_building(self):
        """
        Test verification query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_verification_query(table_name)
        self.assertIn("RECORDTAG IN ('PM', 'P1', 'P5')", query)
        self.assertIn("ORDER BY a.TRANSNO, a.RECORDTAG", query)

    def test_duplicate_detection_query(self):
        """
        Test duplicate detection query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_duplicate_detection_query(table_name)
        self.assertIn("GROUP BY TRANSNO", query)
        self.assertIn("HAVING COUNT(*) > 1", query)
        self.assertIn("LIST(RECORDTAG)", query)

    def test_employee_performance_query(self):
        """
        Test employee performance query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_employee_performance_query(table_name)
        self.assertIn("RECORDTAG = 'PM'", query)
        self.assertIn("GROUP BY a.SCANUSERID", query)
        self.assertIn("TOTAL_TRANSACTIONS", query)

    def test_data_quality_check_query(self):
        """
        Test data quality check query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_data_quality_check_query(table_name)
        self.assertIn("COUNT(*) as TOTAL_RECORDS", query)
        self.assertIn("SUM(CASE WHEN RECORDTAG = 'PM'", query)
        self.assertIn("MIN(TRANSDATE)", query)

    def test_table_existence_check_query(self):
        """
        Test table existence check query building
        """
        query_builder = FFBQueryBuilder()

        query = query_builder.build_table_existence_check()
        self.assertIn("RDB$RELATION_NAME", query)
        self.assertIn("LIKE 'FFBSCANNERDATA%'", query)

    def test_table_count_query(self):
        """
        Test table count query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_table_count_query(table_name)
        self.assertIn("COUNT(*) as RECORD_COUNT", query)
        self.assertIn("FROM FFBSCANNERDATA09", query)

    def test_monthly_data_summary_query(self):
        """
        Test monthly data summary query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_monthly_data_summary_query(table_name)
        self.assertIn("GROUP BY c.DIVNAME", query)
        self.assertIn("TOTAL_TRANSACTIONS", query)
        self.assertIn("SUM(a.TREECOUNT)", query)

    def test_discrepancy_detail_query(self):
        """
        Test discrepancy detail query building
        """
        query_builder = FFBQueryBuilder()
        table_name = "FFBSCANNERDATA09"

        query = query_builder.build_discrepancy_detail_query(table_name)
        self.assertIn("HAVING COUNT(*) > 1", query)
        self.assertIn("ORDER BY a.TRANSNO, a.RECORDTAG", query)

    def test_query_validation(self):
        """
        Test query syntax validation
        """
        query_builder = FFBQueryBuilder()

        # Valid query
        valid_query = "SELECT * FROM table_name"
        is_valid, message = query_builder.validate_query_syntax(valid_query)
        self.assertTrue(is_valid)

        # Empty query
        empty_query = ""
        is_valid, message = query_builder.validate_query_syntax(empty_query)
        self.assertFalse(is_valid)

        # Dangerous query
        dangerous_query = "DROP TABLE table_name"
        is_valid, message = query_builder.validate_query_syntax(dangerous_query)
        self.assertFalse(is_valid)
        self.assertIn("dangerous", message.lower())

    def test_test_query_building(self):
        """
        Test test query building
        """
        query_builder = FFBQueryBuilder()

        query = query_builder.build_test_query()
        self.assertIn("Connection Test Successful", query)
        self.assertIn("CURRENT_TIMESTAMP", query)

    def test_required_tables(self):
        """
        Test getting required tables
        """
        query_builder = FFBQueryBuilder()

        tables = query_builder.get_required_tables()
        self.assertIn('FFBSCANNERDATA', tables)
        self.assertIn('OCFIELD', tables)
        self.assertIn('CRDIVISION', tables)
        self.assertIn('EMP', tables)


class TestFFBConfig(unittest.TestCase):
    """
    Test cases untuk FFBConfig class
    """

    def setUp(self):
        """
        Setup test environment
        """
        self.test_config_dir = "test_config"
        os.makedirs(self.test_config_dir, exist_ok=True)

    def tearDown(self):
        """
        Cleanup test environment
        """
        import shutil
        if os.path.exists(self.test_config_dir):
            shutil.rmtree(self.test_config_dir)

    def test_config_initialization(self):
        """
        Test configuration initialization
        """
        config = FFBConfig(config_dir=self.test_config_dir)

        # Check default configurations are loaded
        self.assertIsNotNone(config.estate_config)
        self.assertIsNotNone(config.report_config)
        self.assertIsNotNone(config.analysis_config)

    def test_estate_config_operations(self):
        """
        Test estate configuration operations
        """
        config = FFBConfig(config_dir=self.test_config_dir)

        # Test getting estate path
        estates = config.get_all_estates()
        self.assertIsInstance(estates, list)
        self.assertGreater(len(estates), 0)

        # Test getting specific estate path
        first_estate = estates[0]
        path = config.get_estate_path(first_estate)
        self.assertIsInstance(path, str)

        # Test updating estate path
        new_path = "new_test_path.fdb"
        config.update_estate_path(first_estate, new_path)
        updated_path = config.get_estate_path(first_estate)
        self.assertEqual(updated_path, new_path)

    def test_table_name_generation(self):
        """
        Test monthly table name generation
        """
        config = FFBConfig()

        self.assertEqual(config.get_table_name_for_month(1), "FFBSCANNERDATA01")
        self.assertEqual(config.get_table_name_for_month(12), "FFBSCANNERDATA12")

    def test_month_list_from_range(self):
        """
        Test getting month list from date range
        """
        config = FFBConfig()

        # Same month
        months = config.get_month_list_from_range("2025-09-01", "2025-09-30")
        self.assertEqual(months, [9])

        # Cross month
        months = config.get_month_list_from_range("2025-09-15", "2025-10-15")
        self.assertEqual(set(months), {9, 10})

    def test_output_path_generation(self):
        """
        Test output path generation
        """
        config = FFBConfig()

        # Test directory path
        dir_path = config.get_output_path()
        self.assertTrue(dir_path.endswith("reports"))

        # Test file path
        file_path = config.get_output_path("test_report.pdf")
        self.assertTrue(file_path.endswith("test_report.pdf"))


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)