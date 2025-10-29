"""
Employee Repository
Handles data access for employee data
"""

from typing import Dict, Any, List, Optional
from .database_repository import DatabaseRepository
from models.employee import Employee, EmployeeRole


class EmployeeRepository(DatabaseRepository):
    """
    Repository for employee data access operations
    """

    def get_all_employees(self) -> List[Employee]:
        """
        Get all employees from EMP table

        :return: List of Employee objects
        """
        if not self.table_exists('EMP'):
            print("EMP table does not exist")
            return []

        query = "SELECT ID, NAME FROM EMP"
        try:
            rows = self.execute_query(query)
            employees = []
            for row in rows:
                try:
                    employee = Employee.from_db_row(row)
                    employees.append(employee)
                except Exception as e:
                    print(f"Error creating employee from row: {e}")
                    continue

            return employees
        except Exception as e:
            print(f"Error retrieving employees: {e}")
            return []

    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID

        :param employee_id: Employee ID
        :return: Employee object or None
        """
        if not self.table_exists('EMP'):
            return None

        query = f"SELECT ID, NAME FROM EMP WHERE ID = '{employee_id}'"
        try:
            rows = self.execute_query(query)
            if rows:
                return Employee.from_db_row(rows[0])
        except Exception as e:
            print(f"Error retrieving employee {employee_id}: {e}")

        return None

    def get_employee_by_name(self, name: str) -> List[Employee]:
        """
        Get employees by name (can return multiple if names are not unique)

        :param name: Employee name
        :return: List of Employee objects
        """
        if not self.table_exists('EMP'):
            return []

        query = f"SELECT ID, NAME FROM EMP WHERE UPPER(NAME) LIKE UPPER('%{name}%')"
        try:
            rows = self.execute_query(query)
            employees = []
            for row in rows:
                try:
                    employee = Employee.from_db_row(row)
                    employees.append(employee)
                except Exception as e:
                    print(f"Error creating employee from row: {e}")
                    continue

            return employees
        except Exception as e:
            print(f"Error retrieving employees by name {name}: {e}")
            return []

    def search_employees(self, search_term: str) -> List[Employee]:
        """
        Search employees by ID or name

        :param search_term: Search term (ID or name)
        :return: List of matching Employee objects
        """
        if not self.table_exists('EMP'):
            return []

        query = f"""
        SELECT ID, NAME FROM EMP
        WHERE ID LIKE '%{search_term}%'
           OR UPPER(NAME) LIKE UPPER('%{search_term}%')
        ORDER BY NAME
        """
        try:
            rows = self.execute_query(query)
            employees = []
            for row in rows:
                try:
                    employee = Employee.from_db_row(row)
                    employees.append(employee)
                except Exception as e:
                    print(f"Error creating employee from row: {e}")
                    continue

            return employees
        except Exception as e:
            print(f"Error searching employees: {e}")
            return []

    def get_employee_count(self) -> int:
        """
        Get total number of employees

        :return: Employee count
        """
        if not self.table_exists('EMP'):
            return 0

        query = "SELECT COUNT(*) as TOTAL FROM EMP"
        try:
            rows = self.execute_query(query)
            if rows:
                return int(rows[0].get('TOTAL', 0))
        except Exception as e:
            print(f"Error getting employee count: {e}")

        return 0

    def get_active_employees(self, transaction_repository,
                            start_date, end_date) -> List[Employee]:
        """
        Get employees who have transactions in the given date range

        :param transaction_repository: TransactionRepository instance
        :param start_date: Start date
        :param end_date: End date
        :return: List of active Employee objects
        """
        # Get all transactions in date range
        transactions = transaction_repository.get_transactions_by_date_range(
            start_date, end_date
        )

        # Get unique user IDs from transactions
        user_ids = set(t.scanuserid for t in transactions)

        # Get employee data for these user IDs
        active_employees = []
        for user_id in user_ids:
            employee = self.get_employee_by_id(user_id)
            if employee:
                active_employees.append(employee)
            else:
                # Create default employee if not found in EMP table
                default_employee = Employee.create_default(user_id)
                active_employees.append(default_employee)

        return active_employees

    def get_or_create_employee(self, employee_id: str,
                              create_if_missing: bool = True) -> Optional[Employee]:
        """
        Get employee by ID, creating default if not found

        :param employee_id: Employee ID
        :param create_if_missing: Whether to create default employee if not found
        :return: Employee object or None
        """
        employee = self.get_employee_by_id(employee_id)

        if not employee and create_if_missing:
            employee = Employee.create_default(employee_id)

        return employee

    def validate_employee_id(self, employee_id: str) -> bool:
        """
        Validate if employee ID exists in EMP table

        :param employee_id: Employee ID to validate
        :return: True if employee exists
        """
        employee = self.get_employee_by_id(employee_id)
        return employee is not None

    def get_employee_mapping(self) -> Dict[str, str]:
        """
        Get mapping of employee ID to name

        :return: Dictionary with employee_id -> employee_name mapping
        """
        employees = self.get_all_employees()
        return {emp.id: emp.name for emp in employees}

    def get_default_employee_mapping(self) -> Dict[str, str]:
        """
        Get default employee mapping for common IDs

        :return: Dictionary with default employee mappings
        """
        return {
            '4771': 'KERANI_DEFAULT',
            '5044': 'ASISTEN_DEFAULT',
            '20001': 'ADMIN_DEFAULT',
            '40389': 'KERANI-40389',
            '40584': 'ASISTEN-40584',
            '40587': 'ASISTEN-40587',
            '40388': 'KERANI-40388',
            '40581': 'ASISTEN-40581',
            '40390': 'KERANI-40390',
            '40583': 'ASISTEN-40583',
            '40391': 'KERANI-40391',
            '40565': 'ASISTEN-40565',
            '40392': 'KERANI-40392'
        }

    def get_complete_employee_mapping(self) -> Dict[str, str]:
        """
        Get complete employee mapping combining database and defaults

        :return: Complete employee mapping
        """
        # Get database mapping
        db_mapping = self.get_employee_mapping()

        # Get default mapping
        default_mapping = self.get_default_employee_mapping()

        # Combine, preferring database mapping
        complete_mapping = default_mapping.copy()
        complete_mapping.update(db_mapping)

        return complete_mapping

    def get_employee_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about employee data

        :return: Dictionary with employee statistics
        """
        if not self.table_exists('EMP'):
            return {
                'total_employees': 0,
                'table_exists': False
            }

        try:
            total_count = self.get_employee_count()
            employees = self.get_all_employees()

            # Count by role (will be determined from transactions)
            role_counts = {
                'KERANI': 0,
                'MANDOR': 0,
                'ASISTEN': 0,
                'UNKNOWN': 0
            }

            # For now, all are unknown until we analyze transactions
            role_counts['UNKNOWN'] = total_count

            return {
                'total_employees': total_count,
                'table_exists': True,
                'role_counts': role_counts,
                'sample_employees': [
                    {
                        'id': emp.id,
                        'name': emp.name
                    }
                    for emp in employees[:5]  # First 5 as sample
                ]
            }
        except Exception as e:
            print(f"Error getting employee statistics: {e}")
            return {
                'total_employees': 0,
                'table_exists': True,
                'error': str(e)
            }

    def bulk_create_employees(self, employee_data: List[Dict[str, Any]]) -> bool:
        """
        Bulk create employees (placeholder for future implementation)

        :param employee_data: List of employee data dictionaries
        :return: True if successful
        """
        # This would be used for creating employees in the database
        # For now, just return True as placeholder
        print(f"Bulk create {len(employee_data)} employees - not implemented yet")
        return True

    def update_employee(self, employee_id: str, name: str) -> bool:
        """
        Update employee name (placeholder for future implementation)

        :param employee_id: Employee ID
        :param name: New name
        :return: True if successful
        """
        # This would be used for updating employee data in the database
        # For now, just return True as placeholder
        print(f"Update employee {employee_id} to {name} - not implemented yet")
        return True