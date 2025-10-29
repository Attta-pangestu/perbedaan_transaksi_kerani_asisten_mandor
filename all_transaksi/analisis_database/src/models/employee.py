"""
Employee Model
Represents employee data with performance metrics
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class EmployeeRole(Enum):
    """Employee role based on transaction types"""
    KERANI = "KERANI"
    MANDOR = "MANDOR"
    ASISTEN = "ASISTEN"
    UNKNOWN = "UNKNOWN"


@dataclass
class Employee:
    """
    Represents an employee in the FFB system
    """
    id: str
    name: str
    role: EmployeeRole = EmployeeRole.UNKNOWN

    # Performance metrics
    kerani_transactions: int = 0
    kerani_verified: int = 0
    kerani_differences: int = 0
    mandor_transactions: int = 0
    asisten_transactions: int = 0

    # Additional metadata
    estate: Optional[str] = None
    division: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Employee':
        """
        Create Employee instance from database row

        :param row: Database row dictionary
        :return: Employee instance
        """
        try:
            emp_id = str(row.get('ID', '')).strip()
            emp_name = str(row.get('NAME', '')).strip()

            if not emp_id:
                raise ValueError("Employee ID is required")

            return cls(
                id=emp_id,
                name=emp_name or f"EMP-{emp_id}",
                role=EmployeeRole.UNKNOWN
            )
        except Exception as e:
            print(f"Error creating employee from row: {e}")
            raise ValueError(f"Invalid employee data: {e}")

    @classmethod
    def create_default(cls, emp_id: str, name: Optional[str] = None) -> 'Employee':
        """
        Create employee with default values

        :param emp_id: Employee ID
        :param name: Employee name (optional)
        :return: Employee instance
        """
        return cls(
            id=emp_id,
            name=name or f"EMP-{emp_id}",
            role=EmployeeRole.UNKNOWN
        )

    def determine_role(self) -> EmployeeRole:
        """
        Determine employee's primary role based on transaction counts

        :return: EmployeeRole
        """
        if self.kerani_transactions > 0:
            return EmployeeRole.KERANI
        elif self.mandor_transactions > 0:
            return EmployeeRole.MANDOR
        elif self.asisten_transactions > 0:
            return EmployeeRole.ASISTEN
        else:
            return EmployeeRole.UNKNOWN

    def get_verification_rate(self) -> float:
        """
        Calculate verification rate for Kerani transactions

        :return: Verification rate percentage
        """
        if self.kerani_transactions == 0:
            return 0.0
        return (self.kerani_verified / self.kerani_transactions) * 100

    def get_difference_rate(self) -> float:
        """
        Calculate difference rate for Kerani transactions

        :return: Difference rate percentage
        """
        if self.kerani_verified == 0:
            return 0.0
        return (self.kerani_differences / self.kerani_verified) * 100

    def get_total_transactions(self) -> int:
        """
        Get total number of transactions across all roles

        :return: Total transaction count
        """
        return self.kerani_transactions + self.mandor_transactions + self.asisten_transactions

    def is_active(self) -> bool:
        """
        Check if employee has any transactions

        :return: True if employee has transactions
        """
        return self.get_total_transactions() > 0

    def is_kerani(self) -> bool:
        """Check if employee has Kerani transactions"""
        return self.kerani_transactions > 0

    def is_mandor(self) -> bool:
        """Check if employee has Mandor transactions"""
        return self.mandor_transactions > 0

    def is_asisten(self) -> bool:
        """Check if employee has Asisten transactions"""
        return self.asisten_transactions > 0

    def get_primary_role_display(self) -> str:
        """
        Get display name for primary role

        :return: Role display name
        """
        role = self.determine_role()
        return role.value if role != EmployeeRole.UNKNOWN else "UNKNOWN"

    def add_kerani_metrics(self, verified: int, differences: int):
        """
        Add Kerani performance metrics

        :param verified: Number of verified transactions
        :param differences: Number of transactions with differences
        """
        self.kerani_transactions += 1
        if verified > 0:
            self.kerani_verified += verified
        if differences > 0:
            self.kerani_differences += differences

    def add_mandor_transaction(self):
        """Increment Mandor transaction count"""
        self.mandor_transactions += 1

    def add_asisten_transaction(self):
        """Increment Asisten transaction count"""
        self.asisten_transactions += 1

    def merge_with(self, other: 'Employee') -> 'Employee':
        """
        Merge this employee with another (aggregates metrics)

        :param other: Another employee to merge with
        :return: New merged employee
        """
        if self.id != other.id:
            raise ValueError(f"Cannot merge employees with different IDs: {self.id} vs {other.id}")

        # Use the non-empty name, preferring the first one
        name = self.name if self.name else (other.name if other.name else f"EMP-{self.id}")

        merged = Employee(
            id=self.id,
            name=name,
            role=self.determine_role(),  # Determine from merged data
            kerani_transactions=self.kerani_transactions + other.kerani_transactions,
            kerani_verified=self.kerani_verified + other.kerani_verified,
            kerani_differences=self.kerani_differences + other.kerani_differences,
            mandor_transactions=self.mandor_transactions + other.mandor_transactions,
            asisten_transactions=self.asisten_transactions + other.asisten_transactions,
            estate=self.estate or other.estate,
            division=self.division or other.division
        )

        return merged

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert employee to dictionary representation

        :return: Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role.value,
            'kerani_transactions': self.kerani_transactions,
            'kerani_verified': self.kerani_verified,
            'kerani_differences': self.kerani_differences,
            'mandor_transactions': self.mandor_transactions,
            'asisten_transactions': self.asisten_transactions,
            'verification_rate': self.get_verification_rate(),
            'difference_rate': self.get_difference_rate(),
            'total_transactions': self.get_total_transactions(),
            'estate': self.estate,
            'division': self.division,
            'is_active': self.is_active(),
            'primary_role': self.get_primary_role_display()
        }

    def get_performance_summary(self) -> str:
        """
        Get performance summary string

        :return: Performance summary
        """
        if not self.is_active():
            return f"{self.name}: No transactions"

        summary_parts = [f"{self.name}"]

        if self.is_kerani():
            summary_parts.append(
                f"Kerani: {self.kerani_transactions} ({self.get_verification_rate():.1f}% verified)"
            )
            if self.kerani_differences > 0:
                summary_parts.append(f"{self.kerani_differences} differences")

        if self.is_mandor():
            summary_parts.append(f"Mandor: {self.mandor_transactions}")

        if self.is_asisten():
            summary_parts.append(f"Asisten: {self.asisten_transactions}")

        return " | ".join(summary_parts)

    def __str__(self) -> str:
        """String representation"""
        return f"Employee[{self.id}] {self.name} ({self.get_primary_role_display()})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Employee(id='{self.id}', name='{self.name}', role={self.role}, "
                f"kerani={self.kerani_transactions}, mandor={self.mandor_transactions}, "
                f"asisten={self.asisten_transactions})")


class EmployeeManager:
    """
    Manages collection of employees with lookup and aggregation capabilities
    """

    def __init__(self):
        self.employees: Dict[str, Employee] = {}

    def add_employee(self, employee: Employee):
        """
        Add or update an employee

        :param employee: Employee to add
        """
        if employee.id in self.employees:
            # Merge with existing employee
            existing = self.employees[employee.id]
            self.employees[employee.id] = existing.merge_with(employee)
        else:
            self.employees[employee.id] = employee

    def get_employee(self, emp_id: str) -> Optional[Employee]:
        """
        Get employee by ID

        :param emp_id: Employee ID
        :return: Employee or None
        """
        return self.employees.get(emp_id)

    def get_or_create_employee(self, emp_id: str, name: Optional[str] = None) -> Employee:
        """
        Get existing employee or create new one

        :param emp_id: Employee ID
        :param name: Employee name (optional)
        :return: Employee instance
        """
        if emp_id in self.employees:
            return self.employees[emp_id]
        else:
            employee = Employee.create_default(emp_id, name)
            self.employees[emp_id] = employee
            return employee

    def get_active_employees(self) -> List[Employee]:
        """
        Get all employees with transactions

        :return: List of active employees
        """
        return [emp for emp in self.employees.values() if emp.is_active()]

    def get_employees_by_role(self, role: EmployeeRole) -> List[Employee]:
        """
        Get employees by role

        :param role: Employee role
        :return: List of employees with specified role
        """
        return [emp for emp in self.employees.values() if emp.determine_role() == role]

    def get_kerani_employees(self) -> List[Employee]:
        """Get all Kerani employees"""
        return self.get_employees_by_role(EmployeeRole.KERANI)

    def get_mandor_employees(self) -> List[Employee]:
        """Get all Mandor employees"""
        return self.get_employees_by_role(EmployeeRole.MANDOR)

    def get_asisten_employees(self) -> List[Employee]:
        """Get all Asisten employees"""
        return self.get_employees_by_role(EmployeeRole.ASISTEN)

    def get_employee_count(self) -> int:
        """Get total employee count"""
        return len(self.employees)

    def get_active_employee_count(self) -> int:
        """Get active employee count"""
        return len(self.get_active_employees())

    def get_totals(self) -> Dict[str, int]:
        """
        Get total transactions by role

        :return: Dictionary with total counts
        """
        totals = {
            'kerani': sum(emp.kerani_transactions for emp in self.employees.values()),
            'mandor': sum(emp.mandor_transactions for emp in self.employees.values()),
            'asisten': sum(emp.asisten_transactions for emp in self.employees.values()),
            'verified': sum(emp.kerani_verified for emp in self.employees.values()),
            'differences': sum(emp.kerani_differences for emp in self.employees.values())
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

    def clear(self):
        """Clear all employees"""
        self.employees.clear()

    def merge_with(self, other: 'EmployeeManager') -> 'EmployeeManager':
        """
        Merge this manager with another

        :param other: Another EmployeeManager to merge with
        :return: New merged EmployeeManager
        """
        merged = EmployeeManager()

        # Add all employees from this manager
        for employee in self.employees.values():
            merged.add_employee(employee)

        # Add all employees from other manager (will merge if IDs match)
        for employee in other.employees.values():
            merged.add_employee(employee)

        return merged

    def __len__(self) -> int:
        """Get number of employees"""
        return len(self.employees)

    def __iter__(self):
        """Iterate over employees"""
        return iter(self.employees.values())

    def __str__(self) -> str:
        """String representation"""
        active = self.get_active_employee_count()
        total = self.get_employee_count()
        return f"EmployeeManager({total} employees, {active} active)"