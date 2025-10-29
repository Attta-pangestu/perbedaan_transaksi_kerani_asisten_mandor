"""
Division Repository
Handles data access for division data
"""

from typing import Dict, Any, List, Optional, Set
from .database_repository import DatabaseRepository
from models.division import Division


class DivisionRepository(DatabaseRepository):
    """
    Repository for division data access operations
    """

    def get_all_divisions(self) -> List[Division]:
        """
        Get all divisions from OCFIELD and CRDIVISION tables

        :return: List of Division objects
        """
        if not self.table_exists('OCFIELD') or not self.table_exists('CRDIVISION'):
            print("OCFIELD or CRDIVISION table does not exist")
            return []

        query = """
        SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
        FROM OCFIELD b
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
        WHERE b.DIVID IS NOT NULL
        """

        try:
            rows = self.execute_query(query)
            divisions = []
            processed_divisions = set()

            for row in rows:
                try:
                    div_id = str(row.get('DIVID', '')).strip()
                    if div_id and div_id not in processed_divisions:
                        division = Division.from_db_row(row)
                        divisions.append(division)
                        processed_divisions.add(div_id)
                except Exception as e:
                    print(f"Error creating division from row: {e}")
                    continue

            return divisions
        except Exception as e:
            print(f"Error retrieving divisions: {e}")
            return []

    def get_division_by_id(self, division_id: str) -> Optional[Division]:
        """
        Get division by ID

        :param division_id: Division ID
        :return: Division object or None
        """
        if not self.table_exists('OCFIELD'):
            return None

        query = f"""
        SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
        FROM OCFIELD b
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
        WHERE b.DIVID = '{division_id}'
        """

        try:
            rows = self.execute_query(query)
            if rows:
                return Division.from_db_row(rows[0])
        except Exception as e:
            print(f"Error retrieving division {division_id}: {e}")

        return None

    def get_division_by_name(self, name: str) -> List[Division]:
        """
        Get divisions by name (can return multiple if names are not unique)

        :param name: Division name
        :return: List of Division objects
        """
        if not self.table_exists('OCFIELD'):
            return []

        query = f"""
        SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
        FROM OCFIELD b
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
        WHERE UPPER(c.DIVNAME) LIKE UPPER('%{name}%')
        """

        try:
            rows = self.execute_query(query)
            divisions = []
            processed_divisions = set()

            for row in rows:
                try:
                    div_id = str(row.get('DIVID', '')).strip()
                    if div_id and div_id not in processed_divisions:
                        division = Division.from_db_row(row)
                        divisions.append(division)
                        processed_divisions.add(div_id)
                except Exception as e:
                    print(f"Error creating division from row: {e}")
                    continue

            return divisions
        except Exception as e:
            print(f"Error retrieving divisions by name {name}: {e}")
            return []

    def search_divisions(self, search_term: str) -> List[Division]:
        """
        Search divisions by ID or name

        :param search_term: Search term (ID or name)
        :return: List of matching Division objects
        """
        if not self.table_exists('OCFIELD'):
            return []

        query = f"""
        SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
        FROM OCFIELD b
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
        WHERE b.DIVID LIKE '%{search_term}%'
           OR UPPER(c.DIVNAME) LIKE UPPER('%{search_term}%')
           OR UPPER(c.DIVCODE) LIKE UPPER('%{search_term}%')
        ORDER BY c.DIVNAME
        """

        try:
            rows = self.execute_query(query)
            divisions = []
            processed_divisions = set()

            for row in rows:
                try:
                    div_id = str(row.get('DIVID', '')).strip()
                    if div_id and div_id not in processed_divisions:
                        division = Division.from_db_row(row)
                        divisions.append(division)
                        processed_divisions.add(div_id)
                except Exception as e:
                    print(f"Error creating division from row: {e}")
                    continue

            return divisions
        except Exception as e:
            print(f"Error searching divisions: {e}")
            return []

    def get_divisions_with_transactions(self, transaction_repository,
                                       start_date, end_date) -> List[Division]:
        """
        Get divisions that have transactions in the given date range

        :param transaction_repository: TransactionRepository instance
        :param start_date: Start date
        :param end_date: End date
        :return: List of Division objects with transaction data
        """
        # Get transactions in date range
        transactions = transaction_repository.get_transactions_by_date_range(
            start_date, end_date
        )

        # Get unique division IDs from transactions
        division_ids = set()
        for transaction in transactions:
            if transaction.divid:
                division_ids.add(str(transaction.divid))

        # Get division data for these division IDs
        divisions_with_data = []
        for div_id in division_ids:
            division = self.get_division_by_id(div_id)
            if division:
                divisions_with_data.append(division)
            else:
                # Create default division if not found in CRDIVISION table
                default_division = Division.create_default(div_id, f"DIV-{div_id}")
                divisions_with_data.append(default_division)

        return divisions_with_data

    def get_division_count(self) -> int:
        """
        Get total number of divisions

        :return: Division count
        """
        if not self.table_exists('OCFIELD'):
            return 0

        query = """
        SELECT COUNT(DISTINCT DIVID) as TOTAL
        FROM OCFIELD
        WHERE DIVID IS NOT NULL
        """

        try:
            rows = self.execute_query(query)
            if rows:
                return int(rows[0].get('TOTAL', 0))
        except Exception as e:
            print(f"Error getting division count: {e}")

        return 0

    def get_division_mapping(self) -> Dict[str, str]:
        """
        Get mapping of division ID to name

        :return: Dictionary with division_id -> division_name mapping
        """
        divisions = self.get_all_divisions()
        return {div.id: div.name for div in divisions}

    def validate_division_id(self, division_id: str) -> bool:
        """
        Validate if division ID exists in database

        :param division_id: Division ID to validate
        :return: True if division exists
        """
        division = self.get_division_by_id(division_id)
        return division is not None

    def get_or_create_division(self, division_id: str,
                              create_if_missing: bool = True) -> Optional[Division]:
        """
        Get division by ID, creating default if not found

        :param division_id: Division ID
        :param create_if_missing: Whether to create default division if not found
        :return: Division object or None
        """
        division = self.get_division_by_id(division_id)

        if not division and create_if_missing:
            division = Division.create_default(division_id)

        return division

    def get_division_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about division data

        :return: Dictionary with division statistics
        """
        if not self.table_exists('OCFIELD'):
            return {
                'total_divisions': 0,
                'table_exists': False
            }

        try:
            total_count = self.get_division_count()
            divisions = self.get_all_divisions()

            # Count divisions with and without names
            named_divisions = sum(1 for div in divisions if div.name and div.name != f"DIV-{div.id}")
            unnamed_divisions = total_count - named_divisions

            return {
                'total_divisions': total_count,
                'table_exists': True,
                'named_divisions': named_divisions,
                'unnamed_divisions': unnamed_divisions,
                'sample_divisions': [
                    {
                        'id': div.id,
                        'name': div.name,
                        'code': div.code
                    }
                    for div in divisions[:5]  # First 5 as sample
                ]
            }
        except Exception as e:
            print(f"Error getting division statistics: {e}")
            return {
                'total_divisions': 0,
                'table_exists': True,
                'error': str(e)
            }

    def get_available_divisions_for_period(self, start_date, end_date,
                                          transaction_repository) -> List[Division]:
        """
        Get divisions that have available data for the specified period

        :param start_date: Start date
        :param end_date: End date
        :param transaction_repository: TransactionRepository instance
        :return: List of available divisions
        """
        return self.get_divisions_with_transactions(transaction_repository,
                                                   start_date, end_date)

    def get_division_field_count(self, division_id: str) -> int:
        """
        Get number of fields in a division

        :param division_id: Division ID
        :return: Number of fields
        """
        if not self.table_exists('OCFIELD'):
            return 0

        query = f"""
        SELECT COUNT(*) as TOTAL
        FROM OCFIELD
        WHERE DIVID = '{division_id}'
        """

        try:
            rows = self.execute_query(query)
            if rows:
                return int(rows[0].get('TOTAL', 0))
        except Exception as e:
            print(f"Error getting field count for division {division_id}: {e}")

        return 0

    def get_complete_division_info(self, division_id: str,
                                  transaction_repository=None,
                                  start_date=None, end_date=None) -> Dict[str, Any]:
        """
        Get complete information about a division

        :param division_id: Division ID
        :param transaction_repository: Optional TransactionRepository for transaction data
        :param start_date: Optional start date for transaction data
        :param end_date: Optional end date for transaction data
        :return: Dictionary with complete division information
        """
        division = self.get_division_by_id(division_id)
        if not division:
            return {'error': f'Division {division_id} not found'}

        info = division.to_dict()

        # Add field count
        info['field_count'] = self.get_division_field_count(division_id)

        # Add transaction data if requested
        if transaction_repository and start_date and end_date:
            try:
                transactions = transaction_repository.get_transactions_by_date_range(
                    start_date, end_date, division_id
                )
                stats = transaction_repository.get_transaction_statistics(transactions)
                info['transaction_stats'] = stats
            except Exception as e:
                info['transaction_error'] = str(e)

        return info