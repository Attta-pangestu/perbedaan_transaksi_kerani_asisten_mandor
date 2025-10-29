"""
Transaction Repository
Handles data access for transaction data
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
from .database_repository import DatabaseRepository
from models.transaction import Transaction, TransactionGroup


class TransactionRepository(DatabaseRepository):
    """
    Repository for transaction data access operations
    """

    def get_transactions_by_date_range(self, start_date: date, end_date: date,
                                      division_id: Optional[str] = None,
                                      month_tables: Optional[List[str]] = None) -> List[Transaction]:
        """
        Get transactions within date range

        :param start_date: Start date
        :param end_date: End date
        :param division_id: Optional division ID filter
        :param month_tables: Optional list of month tables to query
        :return: List of Transaction objects
        """
        if month_tables is None:
            month_tables = self._get_month_tables(start_date, end_date)

        all_transactions = []

        for table_name in month_tables:
            if not self.table_exists(table_name):
                print(f"Table {table_name} does not exist, skipping")
                continue

            try:
                transactions = self._get_transactions_from_table(
                    table_name, start_date, end_date, division_id
                )
                all_transactions.extend(transactions)
                print(f"Retrieved {len(transactions)} transactions from {table_name}")
            except Exception as e:
                print(f"Error retrieving from {table_name}: {e}")
                continue

        # Remove duplicates based on ID
        unique_transactions = {}
        for transaction in all_transactions:
            if transaction.id not in unique_transactions:
                unique_transactions[transaction.id] = transaction

        return list(unique_transactions.values())

    def _get_month_tables(self, start_date: date, end_date: date) -> List[str]:
        """
        Get list of month tables within date range

        :param start_date: Start date
        :param end_date: End date
        :return: List of month table names
        """
        month_tables = []
        current = start_date

        while current <= end_date:
            if current.year == end_date.year:
                # Same year, just add months in range
                table_name = f"FFBSCANNERDATA{current.month:02d}"
                if table_name not in month_tables:
                    month_tables.append(table_name)
            else:
                # Different year, add all remaining months of current year
                for month in range(current.month, 13):
                    table_name = f"FFBSCANNERDATA{month:02d}"
                    if table_name not in month_tables:
                        month_tables.append(table_name)

            # Move to next year if needed
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)

            if current.year > end_date.year:
                break

        return month_tables

    def _get_transactions_from_table(self, table_name: str, start_date: date,
                                    end_date: date, division_id: Optional[str] = None) -> List[Transaction]:
        """
        Get transactions from a specific table

        :param table_name: Table name
        :param start_date: Start date
        :param end_date: End date
        :param division_id: Optional division ID filter
        :return: List of Transaction objects
        """
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Build query with optional division filter
        base_query = f"""
        SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
               a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
               a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
               a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
               a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
               b.DIVID, c.DIVNAME, c.DIVCODE
        FROM {table_name} a
        JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
        WHERE a.TRANSDATE >= '{start_str}' AND a.TRANSDATE <= '{end_str}'
        """

        if division_id:
            base_query += f" AND b.DIVID = '{division_id}'"

        base_query += " ORDER BY c.DIVNAME, a.TRANSNO, a.TRANSDATE, a.TRANSTIME"

        try:
            rows = self.execute_query(base_query)
            transactions = []
            for row in rows:
                try:
                    transaction = Transaction.from_db_row(row)
                    transactions.append(transaction)
                except Exception as e:
                    print(f"Error creating transaction from row: {e}")
                    continue

            return transactions
        except Exception as e:
            print(f"Error executing query on {table_name}: {e}")
            raise

    def find_duplicate_transactions(self, transactions: List[Transaction]) -> Dict[str, TransactionGroup]:
        """
        Find duplicate transactions by TRANSNO

        :param transactions: List of transactions to analyze
        :return: Dictionary with TRANSNO as key and TransactionGroup as value
        """
        # Group transactions by TRANSNO
        transno_groups = {}

        for transaction in transactions:
            if transaction.transno not in transno_groups:
                transno_groups[transaction.transno] = TransactionGroup(transaction.transno)
            transno_groups[transaction.transno].add_transaction(transaction)

        # Filter to only groups with duplicates (more than 1 transaction)
        duplicate_groups = {
            transno: group for transno, group in transno_groups.items()
            if group.size() > 1
        }

        return duplicate_groups

    def get_verified_transactions(self, transactions: List[Transaction],
                                 use_status_filter: bool = False) -> Dict[str, TransactionGroup]:
        """
        Get verified transaction groups

        :param transactions: List of transactions to analyze
        :param use_status_filter: Apply status 704 filter
        :return: Dictionary with TRANSNO as key and verified TransactionGroup as value
        """
        duplicate_groups = self.find_duplicate_transactions(transactions)
        verified_groups = {}

        for transno, group in duplicate_groups.items():
            if group.is_verified(use_status_filter):
                verified_groups[transno] = group

        return verified_groups

    def get_transaction_statistics(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Get statistics for transaction list

        :param transactions: List of transactions
        :return: Dictionary with statistics
        """
        if not transactions:
            return {
                'total_transactions': 0,
                'kerani_count': 0,
                'mandor_count': 0,
                'asisten_count': 0,
                'unique_transnos': 0,
                'duplicate_groups': 0,
                'verified_groups': 0
            }

        # Count by role
        kerani_count = sum(1 for t in transactions if t.is_kerani())
        mandor_count = sum(1 for t in transactions if t.is_mandor())
        asisten_count = sum(1 for t in transactions if t.is_asisten())

        # Find duplicates
        duplicate_groups = self.find_duplicate_transactions(transactions)
        verified_groups = self.get_verified_transactions(transactions)

        return {
            'total_transactions': len(transactions),
            'kerani_count': kerani_count,
            'mandor_count': mandor_count,
            'asisten_count': asisten_count,
            'unique_transnos': len(set(t.transno for t in transactions)),
            'duplicate_groups': len(duplicate_groups),
            'verified_groups': len(verified_groups)
        }

    def get_available_date_range(self) -> Dict[str, Optional[date]]:
        """
        Get available date range from transaction tables

        :return: Dictionary with min_date and max_date
        """
        min_date = None
        max_date = None

        # Check all monthly tables
        for i in range(1, 13):
            table_name = f"FFBSCANNERDATA{i:02d}"
            if not self.table_exists(table_name):
                continue

            try:
                query = f"""
                SELECT MIN(a.TRANSDATE) as MIN_DATE, MAX(a.TRANSDATE) as MAX_DATE
                FROM {table_name} a
                WHERE a.TRANSDATE IS NOT NULL
                """

                rows = self.execute_query(query)
                if rows and rows[0].get('MIN_DATE'):
                    row_min = self._parse_date_from_string(rows[0]['MIN_DATE'])
                    row_max = self._parse_date_from_string(rows[0]['MAX_DATE'])

                    if row_min and (min_date is None or row_min < min_date):
                        min_date = row_min
                    if row_max and (max_date is None or row_max > max_date):
                        max_date = row_max

            except Exception as e:
                print(f"Error getting date range from {table_name}: {e}")
                continue

        return {
            'min_date': min_date,
            'max_date': max_date
        }

    def _parse_date_from_string(self, date_str: str) -> Optional[date]:
        """
        Parse date string from database

        :param date_str: Date string
        :return: Date object or None
        """
        if not date_str:
            return None

        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        except Exception:
            pass

        return None

    def get_transaction_by_transno(self, transno: str,
                                   start_date: date, end_date: date) -> List[Transaction]:
        """
        Get specific transaction by TRANSNO

        :param transno: Transaction number
        :param start_date: Start date
        :param end_date: End date
        :return: List of transactions with given TRANSNO
        """
        transactions = self.get_transactions_by_date_range(start_date, end_date)
        return [t for t in transactions if t.transno == transno]

    def get_transactions_by_user(self, user_id: str, start_date: date,
                                 end_date: date) -> List[Transaction]:
        """
        Get transactions for specific user

        :param user_id: User ID
        :param start_date: Start date
        :param end_date: End date
        :return: List of transactions for user
        """
        transactions = self.get_transactions_by_date_range(start_date, end_date)
        return [t for t in transactions if t.scanuserid == user_id]