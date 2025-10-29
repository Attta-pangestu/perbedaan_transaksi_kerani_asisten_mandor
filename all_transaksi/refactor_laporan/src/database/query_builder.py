"""
Query Builder untuk FFB Scanner Analysis System

Modul ini menyediakan fungsi-fungsi untuk membangun query SQL
yang digunakan untuk mengambil data dari database Firebird.
"""

from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FFBQueryBuilder:
    """
    Query builder untuk FFB database operations
    """

    def __init__(self):
        self.table_prefix = "FFBSCANNERDATA"
        self.required_tables = {
            'FFBSCANNERDATA': 'Main transaction data',
            'OCFIELD': 'Field information',
            'CRDIVISION': 'Division information',
            'EMP': 'Employee information'
        }

    def get_monthly_table_name(self, month: int) -> str:
        """
        Get monthly table name

        Args:
            month: Month number (1-12)

        Returns:
            Table name dengan format FFBSCANNERDATAMM
        """
        return f"{self.table_prefix}{month:02d}"

    def build_base_query(self, table_name: str,
                        start_date: str = None,
                        end_date: str = None,
                        estates: List[str] = None) -> str:
        """
        Build base query untuk mengambil transaksi data

        Args:
            table_name: Monthly table name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            estates: List estate names

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            a.TRANSNO,
            a.SCANUSERID,
            a.RECORDTAG,
            a.TRANSDATE,
            a.FIELDID,
            a.AFD,
            a.BLOCK,
            a.TREECOUNT,
            a.BUNCHCOUNT,
            a.LOOSEFRUIT,
            a.WEIGHT,
            a.TBS,
            a.HARVESTER,
            a.TAKENBY,
            b.DIVID,
            c.DIVNAME,
            d.EMPNAME
        FROM {table_name} a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        LEFT JOIN EMP d ON a.SCANUSERID = d.EMPID
        WHERE 1=1
        """

        # Add date filter
        if start_date:
            query += f" AND a.TRANSDATE >= '{start_date}'"
        if end_date:
            query += f" AND a.TRANSDATE <= '{end_date}'"

        # Add estate filter
        if estates:
            estate_list = "', '".join(estates)
            query += f" AND c.DIVNAME IN ('{estate_list}')"

        # Order by
        query += " ORDER BY a.TRANSDATE, a.TRANSNO"

        return query

    def build_kerani_transactions_query(self, table_name: str,
                                       start_date: str = None,
                                       end_date: str = None,
                                       estates: List[str] = None) -> str:
        """
        Build query untuk mengambil transaksi kerani (PM) saja

        Args:
            table_name: Monthly table name
            start_date: Start date
            end_date: End date
            estates: List estate names

        Returns:
            SQL query string
        """
        base_query = self.build_base_query(table_name, start_date, end_date, estates)
        kerani_query = base_query.replace("WHERE 1=1", "WHERE a.RECORDTAG = 'PM'")
        return kerani_query

    def build_verification_query(self, table_name: str,
                                start_date: str = None,
                                end_date: str = None,
                                estates: List[str] = None) -> str:
        """
        Build query untuk data verifikasi (semua record types)

        Args:
            table_name: Monthly table name
            start_date: Start date
            end_date: End date
            estates: List estate names

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            a.TRANSNO,
            a.SCANUSERID,
            a.RECORDTAG,
            a.TRANSDATE,
            a.FIELDID,
            a.AFD,
            a.BLOCK,
            a.TREECOUNT,
            a.BUNCHCOUNT,
            a.LOOSEFRUIT,
            a.WEIGHT,
            a.TBS,
            a.HARVESTER,
            a.TAKENBY,
            b.DIVID,
            c.DIVNAME,
            d.EMPNAME
        FROM {table_name} a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        LEFT JOIN EMP d ON a.SCANUSERID = d.EMPID
        WHERE a.RECORDTAG IN ('PM', 'P1', 'P5')
        """

        # Add date filter
        if start_date:
            query += f" AND a.TRANSDATE >= '{start_date}'"
        if end_date:
            query += f" AND a.TRANSDATE <= '{end_date}'"

        # Add estate filter
        if estates:
            estate_list = "', '".join(estates)
            query += f" AND c.DIVNAME IN ('{estate_list}')"

        query += " ORDER BY a.TRANSNO, a.RECORDTAG"

        return query

    def build_duplicate_detection_query(self, table_name: str,
                                       start_date: str = None,
                                       end_date: str = None) -> str:
        """
        Build query untuk deteksi duplikat berdasarkan TRANSNO

        Args:
            table_name: Monthly table name
            start_date: Start date
            end_date: End date

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            TRANSNO,
            COUNT(*) as DUPLICATE_COUNT,
            LIST(RECORDTAG) as RECORD_TYPES,
            LIST(SCANUSERID) as USER_IDS
        FROM {table_name}
        WHERE 1=1
        """

        if start_date:
            query += f" AND TRANSDATE >= '{start_date}'"
        if end_date:
            query += f" AND TRANSDATE <= '{end_date}'"

        query += """
        GROUP BY TRANSNO
        HAVING COUNT(*) > 1
        ORDER BY DUPLICATE_COUNT DESC
        """

        return query

    def build_employee_performance_query(self, table_name: str,
                                        start_date: str = None,
                                        end_date: str = None,
                                        estates: List[str] = None) -> str:
        """
        Build query untuk performa karyawan

        Args:
            table_name: Monthly table name
            start_date: Start date
            end_date: End date
            estates: List estate names

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            a.SCANUSERID,
            d.EMPNAME,
            c.DIVNAME,
            COUNT(*) as TOTAL_TRANSACTIONS,
            COUNT(DISTINCT a.TRANSNO) as UNIQUE_TRANSNO,
            MIN(a.TRANSDATE) as FIRST_TRANSACTION,
            MAX(a.TRANSDATE) as LAST_TRANSACTION
        FROM {table_name} a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        LEFT JOIN EMP d ON a.SCANUSERID = d.EMPID
        WHERE a.RECORDTAG = 'PM'
        """

        if start_date:
            query += f" AND a.TRANSDATE >= '{start_date}'"
        if end_date:
            query += f" AND a.TRANSDATE <= '{end_date}'"

        if estates:
            estate_list = "', '".join(estates)
            query += f" AND c.DIVNAME IN ('{estate_list}')"

        query += """
        GROUP BY a.SCANUSERID, d.EMPNAME, c.DIVNAME
        ORDER BY TOTAL_TRANSACTIONS DESC
        """

        return query

    def build_data_quality_check_query(self, table_name: str) -> str:
        """
        Build query untuk quality check data

        Args:
            table_name: Monthly table name

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            COUNT(*) as TOTAL_RECORDS,
            COUNT(DISTINCT TRANSNO) as UNIQUE_TRANSNO,
            SUM(CASE WHEN RECORDTAG = 'PM' THEN 1 ELSE 0 END) as PM_RECORDS,
            SUM(CASE WHEN RECORDTAG = 'P1' THEN 1 ELSE 0 END) as P1_RECORDS,
            SUM(CASE WHEN RECORDTAG = 'P5' THEN 1 ELSE 0 END) as P5_RECORDS,
            SUM(CASE WHEN TRANSDATE IS NULL THEN 1 ELSE 0 END) as NULL_DATE_COUNT,
            SUM(CASE WHEN FIELDID IS NULL OR FIELDID = '' THEN 1 ELSE 0 END) as NULL_FIELD_COUNT,
            SUM(CASE WHEN SCANUSERID IS NULL OR SCANUSERID = '' THEN 1 ELSE 0 END) as NULL_USER_COUNT,
            MIN(TRANSDATE) as MIN_DATE,
            MAX(TRANSDATE) as MAX_DATE
        FROM {table_name}
        """

        return query

    def build_table_existence_check(self) -> str:
        """
        Build query untuk mengecek apakah table exists

        Returns:
            SQL query string
        """
        return """
        SELECT RDB$RELATION_NAME as TABLE_NAME
        FROM RDB$RELATIONS
        WHERE RDB$RELATION_NAME LIKE 'FFBSCANNERDATA%'
        ORDER BY RDB$RELATION_NAME
        """

    def build_table_count_query(self, table_name: str) -> str:
        """
        Build query untuk menghitung jumlah records di table

        Args:
            table_name: Table name

        Returns:
            SQL query string
        """
        return f"SELECT COUNT(*) as RECORD_COUNT FROM {table_name}"

    def build_monthly_data_summary_query(self, table_name: str,
                                        start_date: str = None,
                                        end_date: str = None) -> str:
        """
        Build query untuk summary data bulanan

        Args:
            table_name: Monthly table name
            start_date: Start date
            end_date: End date

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            c.DIVNAME,
            COUNT(*) as TOTAL_TRANSACTIONS,
            COUNT(DISTINCT a.TRANSNO) as UNIQUE_TRANSNO,
            COUNT(DISTINCT a.SCANUSERID) as ACTIVE_USERS,
            SUM(CASE WHEN a.RECORDTAG = 'PM' THEN 1 ELSE 0 END) as PM_COUNT,
            SUM(CASE WHEN a.RECORDTAG = 'P1' THEN 1 ELSE 0 END) as P1_COUNT,
            SUM(CASE WHEN a.RECORDTAG = 'P5' THEN 1 ELSE 0 END) as P5_COUNT,
            SUM(a.TREECOUNT) as TOTAL_TREES,
            SUM(a.BUNCHCOUNT) as TOTAL_BUNCHES,
            SUM(a.WEIGHT) as TOTAL_WEIGHT
        FROM {table_name} a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        WHERE 1=1
        """

        if start_date:
            query += f" AND a.TRANSDATE >= '{start_date}'"
        if end_date:
            query += f" AND a.TRANSDATE <= '{end_date}'"

        query += """
        GROUP BY c.DIVNAME
        ORDER BY TOTAL_TRANSACTIONS DESC
        """

        return query

    def build_discrepancy_detail_query(self, table_name: str,
                                     start_date: str = None,
                                     end_date: str = None) -> str:
        """
        Build query untuk detail discrepancy analysis

        Args:
            table_name: Monthly table name
            start_date: Start date
            end_date: End date

        Returns:
            SQL query string
        """
        query = f"""
        SELECT
            a.TRANSNO,
            a.RECORDTAG,
            a.SCANUSERID,
            a.AFD,
            a.BLOCK,
            a.TREECOUNT,
            a.BUNCHCOUNT,
            a.LOOSEFRUIT,
            a.WEIGHT,
            a.TBS,
            a.HARVESTER,
            a.TAKENBY,
            d.EMPNAME,
            c.DIVNAME
        FROM {table_name} a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        LEFT JOIN EMP d ON a.SCANUSERID = d.EMPID
        WHERE a.TRANSNO IN (
            SELECT TRANSNO
            FROM {table_name}
            WHERE 1=1
        """

        if start_date:
            query += f" AND TRANSDATE >= '{start_date}'"
        if end_date:
            query += f" AND TRANSDATE <= '{end_date}'"

        query += """
            GROUP BY TRANSNO
            HAVING COUNT(*) > 1
        )
        ORDER BY a.TRANSNO, a.RECORDTAG
        """

        return query

    def get_required_tables(self) -> Dict[str, str]:
        """
        Get list required tables dengan deskripsi

        Returns:
            Dict dengan table name dan deskripsi
        """
        return self.required_tables

    def validate_query_syntax(self, query: str) -> Tuple[bool, str]:
        """
        Validasi syntax query secara basic

        Args:
            query: SQL query string

        Returns:
            Tuple (is_valid, error_message)
        """
        if not query.strip():
            return False, "Query is empty"

        # Basic validation - check for required keywords
        if not any(keyword in query.upper() for keyword in ['SELECT', 'SHOW']):
            return False, "Query must start with SELECT or SHOW"

        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if keyword in query.upper():
                return False, f"Query contains dangerous keyword: {keyword}"

        return True, "Query syntax appears valid"

    def build_test_query(self) -> str:
        """
        Build simple test query untuk database connection test

        Returns:
            Simple test query
        """
        return """
        SELECT
            'Connection Test Successful' as STATUS,
            CURRENT_TIMESTAMP as TEST_TIME
        FROM RDB$DATABASE
        """