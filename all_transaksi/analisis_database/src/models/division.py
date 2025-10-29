"""
Division Model
Represents division data with employee and transaction summaries
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .employee import Employee, EmployeeManager
from .transaction import Transaction


@dataclass
class Division:
    """
    Represents a division in the FFB system
    """
    id: str
    name: str
    code: Optional[str] = None
    estate: Optional[str] = None

    # Employee management
    employee_manager: EmployeeManager = field(default_factory=EmployeeManager)

    # Transaction summaries
    total_transactions: int = 0
    kerani_transactions: int = 0
    mandor_transactions: int = 0
    asisten_transactions: int = 0
    verified_transactions: int = 0
    differences_count: int = 0

    @classmethod
    def from_db_row(cls, row: Dict[str, Any], estate_name: Optional[str] = None) -> 'Division':
        """
        Create Division instance from database row

        :param row: Database row dictionary
        :param estate_name: Estate name (optional)
        :return: Division instance
        """
        try:
            div_id = str(row.get('ID', '')).strip()
            div_name = str(row.get('DIVNAME', '')).strip()
            div_code = str(row.get('DIVCODE', '')).strip() or None

            if not div_id:
                raise ValueError("Division ID is required")

            return cls(
                id=div_id,
                name=div_name or f"DIV-{div_id}",
                code=div_code,
                estate=estate_name
            )
        except Exception as e:
            print(f"Error creating division from row: {e}")
            raise ValueError(f"Invalid division data: {e}")

    @classmethod
    def create_default(cls, div_id: str, div_name: Optional[str] = None) -> 'Division':
        """
        Create division with default values

        :param div_id: Division ID
        :param div_name: Division name (optional)
        :return: Division instance
        """
        return cls(
            id=div_id,
            name=div_name or f"DIV-{div_id}"
        )

    def add_employee(self, employee: Employee):
        """
        Add an employee to this division

        :param employee: Employee to add
        """
        # Set division context for employee
        employee.division = self.name
        if self.estate:
            employee.estate = self.estate

        self.employee_manager.add_employee(employee)

        # Update division totals based on employee data
        self.kerani_transactions += employee.kerani_transactions
        self.mandor_transactions += employee.mandor_transactions
        self.asisten_transactions += employee.asisten_transactions
        self.verified_transactions += employee.kerani_verified
        self.differences_count += employee.kerani_differences

        # Update total transactions (Kerani only for division calculations)
        self.total_transactions = self.kerani_transactions

    def get_verification_rate(self) -> float:
        """
        Calculate verification rate for this division

        :return: Verification rate percentage
        """
        if self.kerani_transactions == 0:
            return 0.0
        return (self.verified_transactions / self.kerani_transactions) * 100

    def get_difference_rate(self) -> float:
        """
        Calculate difference rate for this division

        :return: Difference rate percentage
        """
        if self.verified_transactions == 0:
            return 0.0
        return (self.differences_count / self.verified_transactions) * 100

    def get_active_employees(self) -> List[Employee]:
        """
        Get all active employees in this division

        :return: List of active employees
        """
        return self.employee_manager.get_active_employees()

    def get_employees_by_role(self, role: str) -> List[Employee]:
        """
        Get employees by role in this division

        :param role: Role name ('KERANI', 'MANDOR', 'ASISTEN')
        :return: List of employees with specified role
        """
        from .employee import EmployeeRole
        try:
            role_enum = EmployeeRole(role)
            return self.employee_manager.get_employees_by_role(role_enum)
        except ValueError:
            return []

    def get_kerani_employees(self) -> List[Employee]:
        """Get all Kerani employees in this division"""
        return self.employee_manager.get_kerani_employees()

    def get_mandor_employees(self) -> List[Employee]:
        """Get all Mandor employees in this division"""
        return self.employee_manager.get_mandor_employees()

    def get_asisten_employees(self) -> List[Employee]:
        """Get all Asisten employees in this division"""
        return self.employee_manager.get_asisten_employees()

    def get_employee_count(self) -> int:
        """Get total employee count in this division"""
        return self.employee_manager.get_employee_count()

    def get_active_employee_count(self) -> int:
        """Get active employee count in this division"""
        return self.employee_manager.get_active_employee_count()

    def has_data(self) -> bool:
        """
        Check if this division has any transaction data

        :return: True if division has data
        """
        return self.total_transactions > 0

    def get_summary_dict(self) -> Dict[str, Any]:
        """
        Get summary statistics for this division

        :return: Dictionary with summary statistics
        """
        return {
            'division_id': self.id,
            'division_name': self.name,
            'division_code': self.code,
            'estate': self.estate,
            'employee_count': self.get_employee_count(),
            'active_employee_count': self.get_active_employee_count(),
            'total_transactions': self.total_transactions,
            'kerani_transactions': self.kerani_transactions,
            'mandor_transactions': self.mandor_transactions,
            'asisten_transactions': self.asisten_transactions,
            'verified_transactions': self.verified_transactions,
            'differences_count': self.differences_count,
            'verification_rate': self.get_verification_rate(),
            'difference_rate': self.get_difference_rate(),
            'has_data': self.has_data()
        }

    def get_performance_ranking(self) -> List[Employee]:
        """
        Get employees ranked by verification performance

        :return: List of employees sorted by verification rate
        """
        employees = self.get_active_employees()
        # Sort by verification rate (descending), then by transaction count (descending)
        return sorted(
            employees,
            key=lambda emp: (emp.get_verification_rate(), emp.kerani_transactions),
            reverse=True
        )

    def get_problematic_employees(self, min_differences: int = 1) -> List[Employee]:
        """
        Get employees with data quality issues

        :param min_differences: Minimum number of differences to be considered problematic
        :return: List of employees with quality issues
        """
        return [
            emp for emp in self.get_kerani_employees()
            if emp.kerani_differences >= min_differences
        ]

    def add_transaction_metrics(self, kerani_count: int = 0, mandor_count: int = 0,
                              asisten_count: int = 0, verified_count: int = 0,
                              differences_count: int = 0):
        """
        Add transaction metrics directly to division

        :param kerani_count: Number of Kerani transactions
        :param mandor_count: Number of Mandor transactions
        :param asisten_count: Number of Asisten transactions
        :param verified_count: Number of verified transactions
        :param differences_count: Number of transactions with differences
        """
        self.kerani_transactions += kerani_count
        self.mandor_transactions += mandor_count
        self.asisten_transactions += asisten_count
        self.verified_transactions += verified_count
        self.differences_count += differences_count
        self.total_transactions = self.kerani_transactions

    def merge_with(self, other: 'Division') -> 'Division':
        """
        Merge this division with another (aggregates all data)

        :param other: Another division to merge with
        :return: New merged division
        """
        if self.id != other.id:
            raise ValueError(f"Cannot merge divisions with different IDs: {self.id} vs {other.id}")

        # Use the non-empty name, preferring the first one
        name = self.name if self.name else (other.name if other.name else f"DIV-{self.id}")
        code = self.code or other.code
        estate = self.estate or other.estate

        merged = Division(
            id=self.id,
            name=name,
            code=code,
            estate=estate
        )

        # Merge employee managers
        merged.employee_manager = self.employee_manager.merge_with(other.employee_manager)

        # Aggregate transaction metrics
        merged.kerani_transactions = self.kerani_transactions + other.kerani_transactions
        merged.mandor_transactions = self.mandor_transactions + other.mandor_transactions
        merged.asisten_transactions = self.asisten_transactions + other.asisten_transactions
        merged.verified_transactions = self.verified_transactions + other.verified_transactions
        merged.differences_count = self.differences_count + other.differences_count
        merged.total_transactions = merged.kerani_transactions

        return merged

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert division to dictionary representation

        :return: Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'estate': self.estate,
            'summary': self.get_summary_dict(),
            'employees': [emp.to_dict() for emp in self.get_active_employees()]
        }

    def __str__(self) -> str:
        """String representation"""
        estate_prefix = f"{self.estate} - " if self.estate else ""
        return f"Division[{self.id}] {estate_prefix}{self.name}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Division(id='{self.id}', name='{self.name}', code='{self.code}', "
                f"estate='{self.estate}', employees={self.get_active_employee_count()}, "
                f"transactions={self.total_transactions})")


class DivisionManager:
    """
    Manages collection of divisions with lookup and aggregation capabilities
    """

    def __init__(self):
        self.divisions: Dict[str, Division] = {}

    def add_division(self, division: Division):
        """
        Add or update a division

        :param division: Division to add
        """
        if division.id in self.divisions:
            # Merge with existing division
            existing = self.divisions[division.id]
            self.divisions[division.id] = existing.merge_with(division)
        else:
            self.divisions[division.id] = division

    def get_division(self, div_id: str) -> Optional[Division]:
        """
        Get division by ID

        :param div_id: Division ID
        :return: Division or None
        """
        return self.divisions.get(div_id)

    def get_or_create_division(self, div_id: str, div_name: Optional[str] = None) -> Division:
        """
        Get existing division or create new one

        :param div_id: Division ID
        :param div_name: Division name (optional)
        :return: Division instance
        """
        if div_id in self.divisions:
            return self.divisions[div_id]
        else:
            division = Division.create_default(div_id, div_name)
            self.divisions[div_id] = division
            return division

    def get_active_divisions(self) -> List[Division]:
        """
        Get all divisions with transaction data

        :return: List of active divisions
        """
        return [div for div in self.divisions.values() if div.has_data()]

    def get_division_count(self) -> int:
        """Get total division count"""
        return len(self.divisions)

    def get_active_division_count(self) -> int:
        """Get active division count"""
        return len(self.get_active_divisions())

    def get_totals(self) -> Dict[str, Any]:
        """
        Get total transaction counts across all divisions

        :return: Dictionary with total counts
        """
        totals = {
            'divisions': self.get_division_count(),
            'active_divisions': self.get_active_division_count(),
            'kerani': sum(div.kerani_transactions for div in self.divisions.values()),
            'mandor': sum(div.mandor_transactions for div in self.divisions.values()),
            'asisten': sum(div.asisten_transactions for div in self.divisions.values()),
            'verified': sum(div.verified_transactions for div in self.divisions.values()),
            'differences': sum(div.differences_count for div in self.divisions.values())
        }

        # Calculate overall verification rate
        if totals['kerani'] > 0:
            totals['verification_rate'] = (totals['verified'] / totals['kerani']) * 100
        else:
            totals['verification_rate'] = 0.0

        # Calculate overall difference rate
        if totals['verified'] > 0:
            totals['difference_rate'] = (totals['differences'] / totals['verified']) * 100
        else:
            totals['difference_rate'] = 0.0

        return totals

    def get_all_employees(self) -> EmployeeManager:
        """
        Get all employees from all divisions

        :return: EmployeeManager with all employees
        """
        all_employees = EmployeeManager()
        for division in self.divisions.values():
            for employee in division.employee_manager.employees.values():
                all_employees.add_employee(employee)
        return all_employees

    def clear(self):
        """Clear all divisions"""
        self.divisions.clear()

    def __len__(self) -> int:
        """Get number of divisions"""
        return len(self.divisions)

    def __iter__(self):
        """Iterate over divisions"""
        return iter(self.divisions.values())

    def __str__(self) -> str:
        """String representation"""
        active = self.get_active_division_count()
        total = self.get_division_count()
        return f"DivisionManager({total} divisions, {active} active)"