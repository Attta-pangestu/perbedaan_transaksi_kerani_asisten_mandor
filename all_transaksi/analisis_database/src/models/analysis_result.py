"""
Analysis Result Models
Contains models for storing and managing analysis results
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .employee import Employee, EmployeeManager
from .division import Division
from .estate import Estate


@dataclass
class EmployeeMetrics:
    """
    Performance metrics for a single employee
    """
    employee_id: str
    employee_name: str
    estate: str
    division: str

    # Transaction counts
    kerani_transactions: int = 0
    kerani_verified: int = 0
    kerani_differences: int = 0
    mandor_transactions: int = 0
    asisten_transactions: int = 0

    # Calculated metrics
    verification_rate: float = 0.0
    difference_rate: float = 0.0

    # Properties for template compatibility
    @property
    def role(self) -> str:
        """Determine primary role based on transaction counts"""
        if self.kerani_transactions > 0:
            return 'Kerani'
        elif self.mandor_transactions > 0:
            return 'Mandor'
        elif self.asisten_transactions > 0:
            return 'Asisten'
        else:
            return 'Unknown'

    @property
    def total_transactions(self) -> int:
        """Get total transactions for primary role"""
        if self.role == 'Kerani':
            return self.kerani_transactions
        elif self.role == 'Mandor':
            return self.mandor_transactions
        elif self.role == 'Asisten':
            return self.asisten_transactions
        return 0

    @property
    def verified_count(self) -> int:
        """Get verified transaction count"""
        return self.kerani_verified

    @property
    def differences_count(self) -> int:
        """Get differences count"""
        return self.kerani_differences

    @classmethod
    def from_employee(cls, employee: Employee) -> 'EmployeeMetrics':
        """
        Create EmployeeMetrics from Employee instance

        :param employee: Employee instance
        :return: EmployeeMetrics instance
        """
        return cls(
            employee_id=employee.id,
            employee_name=employee.name,
            estate=employee.estate or "",
            division=employee.division or "",
            kerani_transactions=employee.kerani_transactions,
            kerani_verified=employee.kerani_verified,
            kerani_differences=employee.kerani_differences,
            mandor_transactions=employee.mandor_transactions,
            asisten_transactions=employee.asisten_transactions,
            verification_rate=employee.get_verification_rate(),
            difference_rate=employee.get_difference_rate()
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation

        :return: Dictionary representation
        """
        return {
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'estate': self.estate,
            'division': self.division,
            'kerani_transactions': self.kerani_transactions,
            'kerani_verified': self.kerani_verified,
            'kerani_differences': self.kerani_differences,
            'mandor_transactions': self.mandor_transactions,
            'asisten_transactions': self.asisten_transactions,
            'verification_rate': self.verification_rate,
            'difference_rate': self.difference_rate
        }


@dataclass
class DivisionSummary:
    """
    Summary metrics for a single division
    """
    estate_name: str
    division_id: str
    division_name: str

    # Transaction totals
    kerani_total: int = 0
    mandor_total: int = 0
    asisten_total: int = 0
    verification_total: int = 0

    # Calculated metrics
    verification_rate: float = 0.0
    difference_count: int = 0
    difference_rate: float = 0.0

    # Employee breakdown
    employee_count: int = 0
    employee_details: Dict[str, EmployeeMetrics] = field(default_factory=dict)

    @classmethod
    def from_division(cls, division: Division) -> 'DivisionSummary':
        """
        Create DivisionSummary from Division instance

        :param division: Division instance
        :return: DivisionSummary instance
        """
        # Convert employees to metrics
        employee_metrics = {}
        for employee in division.get_active_employees():
            employee_metrics[employee.id] = EmployeeMetrics.from_employee(employee)

        return cls(
            estate_name=division.estate or "",
            division_id=division.id,
            division_name=division.name,
            kerani_total=division.kerani_transactions,
            mandor_total=division.mandor_transactions,
            asisten_total=division.asisten_transactions,
            verification_total=division.verified_transactions,
            verification_rate=division.get_verification_rate(),
            difference_count=division.differences_count,
            difference_rate=division.get_difference_rate(),
            employee_count=division.get_active_employee_count(),
            employee_details=employee_metrics
        )

    def get_employee_metrics(self) -> List[EmployeeMetrics]:
        """
        Get all employee metrics

        :return: List of employee metrics
        """
        return list(self.employee_details.values())

    def get_kerani_employees(self) -> List[EmployeeMetrics]:
        """Get Kerani employee metrics"""
        return [emp for emp in self.employee_details.values() if emp.kerani_transactions > 0]

    def get_mandor_employees(self) -> List[EmployeeMetrics]:
        """Get Mandor employee metrics"""
        return [emp for emp in self.employee_details.values() if emp.mandor_transactions > 0]

    def get_asisten_employees(self) -> List[EmployeeMetrics]:
        """Get Asisten employee metrics"""
        return [emp for emp in self.employee_details.values() if emp.asisten_transactions > 0]

    def get_problematic_employees(self, min_differences: int = 1) -> List[EmployeeMetrics]:
        """
        Get employees with quality issues

        :param min_differences: Minimum differences to be considered problematic
        :return: List of problematic employees
        """
        return [emp for emp in self.get_kerani_employees() if emp.kerani_differences >= min_differences]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation

        :return: Dictionary representation
        """
        return {
            'estate_name': self.estate_name,
            'division_id': self.division_id,
            'division_name': self.division_name,
            'kerani_total': self.kerani_total,
            'mandor_total': self.mandor_total,
            'asisten_total': self.asisten_total,
            'verification_total': self.verification_total,
            'verification_rate': self.verification_rate,
            'difference_count': self.difference_count,
            'difference_rate': self.difference_rate,
            'employee_count': self.employee_count,
            'employees': [emp.to_dict() for emp in self.get_employee_metrics()]
        }

    def __str__(self) -> str:
        """String representation"""
        return (f"DivisionSummary[{self.division_name}] "
                f"{self.kerani_total} Kerani ({self.verification_rate:.1f}% verified)")


@dataclass
class AnalysisResult:
    """
    Complete analysis result for one or more estates
    """
    analysis_date: date
    start_date: date
    end_date: date
    analyzed_estates: List[str]

    # Grand totals
    total_estates: int = 0
    total_divisions: int = 0
    grand_kerani: int = 0
    grand_mandor: int = 0
    grand_asisten: int = 0
    grand_kerani_verified: int = 0
    grand_differences: int = 0

    # Calculated rates
    grand_verification_rate: float = 0.0
    grand_difference_rate: float = 0.0

    # Detailed breakdown
    division_summaries: Dict[str, DivisionSummary] = field(default_factory=dict)

    # Analysis metadata
    analysis_duration_seconds: float = 0.0
    use_status_704_filter: bool = False
    analysis_version: str = "1.0"

    # Properties for template compatibility
    @property
    def estate_name(self) -> str:
        """Get primary estate name (for single estate analysis)"""
        return self.analyzed_estates[0] if self.analyzed_estates else ""

    @property
    def employee_metrics(self) -> List[EmployeeMetrics]:
        """Get all employee metrics across all divisions"""
        all_employees = []
        for division_summary in self.get_division_summaries():
            all_employees.extend(division_summary.get_employee_metrics())
        return all_employees

    @classmethod
    def create_empty(cls, start_date: date, end_date: date,
                     estate_names: List[str]) -> 'AnalysisResult':
        """
        Create empty analysis result

        :param start_date: Analysis start date
        :param end_date: Analysis end date
        :param estate_names: List of analyzed estate names
        :return: AnalysisResult instance
        """
        return cls(
            analysis_date=date.today(),
            start_date=start_date,
            end_date=end_date,
            analyzed_estates=estate_names,
            total_estates=len(estate_names)
        )

    def add_division_summary(self, summary: DivisionSummary):
        """
        Add division summary to analysis result

        :param summary: DivisionSummary to add
        """
        key = f"{summary.estate_name}_{summary.division_id}"
        self.division_summaries[key] = summary

        # Update grand totals
        self.total_divisions = len(self.division_summaries)
        self.grand_kerani += summary.kerani_total
        self.grand_mandor += summary.mandor_total
        self.grand_asisten += summary.asisten_total
        self.grand_kerani_verified += summary.verification_total
        self.grand_differences += summary.difference_count

        # Recalculate rates
        self.grand_verification_rate = (self.grand_kerani_verified / self.grand_kerani * 100) if self.grand_kerani > 0 else 0.0
        self.grand_difference_rate = (self.grand_differences / self.grand_kerani_verified * 100) if self.grand_kerani_verified > 0 else 0.0

    def get_division_summaries(self) -> List[DivisionSummary]:
        """
        Get all division summaries

        :return: List of division summaries
        """
        return list(self.division_summaries.values())

    def get_estate_summaries(self) -> Dict[str, List[DivisionSummary]]:
        """
        Get division summaries grouped by estate

        :return: Dictionary with estate names as keys
        """
        estate_summaries = {}
        for summary in self.division_summaries.values():
            estate = summary.estate_name
            if estate not in estate_summaries:
                estate_summaries[estate] = []
            estate_summaries[estate].append(summary)
        return estate_summaries

    def get_all_employee_metrics(self) -> List[EmployeeMetrics]:
        """
        Get all employee metrics from all divisions

        :return: List of all employee metrics
        """
        all_employees = []
        for summary in self.division_summaries.values():
            all_employees.extend(summary.get_employee_metrics())
        return all_employees

    def get_top_performers(self, limit: int = 10) -> List[EmployeeMetrics]:
        """
        Get top performing employees by verification rate

        :param limit: Maximum number of employees to return
        :return: List of top performing employees
        """
        employees = self.get_all_employee_metrics()
        # Filter to Kerani employees only and sort by verification rate
        kerani_employees = [emp for emp in employees if emp.kerani_transactions > 0]
        kerani_employees.sort(key=lambda emp: emp.verification_rate, reverse=True)
        return kerani_employees[:limit]

    def get_problematic_employees(self, min_differences: int = 1, limit: int = 10) -> List[EmployeeMetrics]:
        """
        Get employees with quality issues

        :param min_differences: Minimum differences to be considered problematic
        :param limit: Maximum number of employees to return
        :return: List of problematic employees
        """
        all_employees = []
        for summary in self.division_summaries.values():
            all_employees.extend(summary.get_problematic_employees(min_differences))

        # Sort by difference rate (descending)
        all_employees.sort(key=lambda emp: emp.difference_rate, reverse=True)
        return all_employees[:limit]

    def get_low_performers(self, limit: int = 10) -> List[EmployeeMetrics]:
        """
        Get lowest performing employees by verification rate

        :param limit: Maximum number of employees to return
        :return: List of low performing employees
        """
        employees = self.get_all_employee_metrics()
        # Filter to Kerani employees with transactions and sort by verification rate
        kerani_employees = [emp for emp in employees if emp.kerani_transactions > 0]
        kerani_employees.sort(key=lambda emp: emp.verification_rate)
        return kerani_employees[:limit]

    def get_estate_totals(self, estate_name: str) -> Dict[str, Any]:
        """
        Get total metrics for a specific estate

        :param estate_name: Estate name
        :return: Dictionary with estate totals
        """
        estate_divisions = [s for s in self.division_summaries.values() if s.estate_name == estate_name]

        if not estate_divisions:
            return {}

        totals = {
            'estate_name': estate_name,
            'division_count': len(estate_divisions),
            'kerani_total': sum(d.kerani_total for d in estate_divisions),
            'mandor_total': sum(d.mandor_total for d in estate_divisions),
            'asisten_total': sum(d.asisten_total for d in estate_divisions),
            'verification_total': sum(d.verification_total for d in estate_divisions),
            'differences_count': sum(d.difference_count for d in estate_divisions)
        }

        # Calculate rates
        totals['verification_rate'] = (totals['verification_total'] / totals['kerani_total'] * 100) if totals['kerani_total'] > 0 else 0.0
        totals['difference_rate'] = (totals['differences_count'] / totals['verification_total'] * 100) if totals['verification_total'] > 0 else 0.0

        return totals

    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get overall analysis summary

        :return: Dictionary with analysis summary
        """
        return {
            'analysis_date': self.analysis_date.isoformat(),
            'period': {
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat(),
                'days': (self.end_date - self.start_date).days + 1
            },
            'estates': {
                'analyzed': self.analyzed_estates,
                'total_count': self.total_estates,
                'active_count': len(self.get_estate_summaries())
            },
            'divisions': {
                'total_count': self.total_divisions,
                'active_count': len(self.division_summaries)
            },
            'grand_totals': {
                'kerani': self.grand_kerani,
                'mandor': self.grand_mandor,
                'asisten': self.grand_asisten,
                'verified': self.grand_kerani_verified,
                'differences': self.grand_differences,
                'verification_rate': self.grand_verification_rate,
                'difference_rate': self.grand_difference_rate
            },
            'metadata': {
                'analysis_duration_seconds': self.analysis_duration_seconds,
                'use_status_704_filter': self.use_status_704_filter,
                'analysis_version': self.analysis_version
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to complete dictionary representation

        :return: Dictionary representation
        """
        return {
            'summary': self.get_analysis_summary(),
            'divisions': {key: summary.to_dict() for key, summary in self.division_summaries.items()},
            'estates': {estate: [d.to_dict() for d in divisions]
                       for estate, divisions in self.get_estate_summaries().items()},
            'top_performers': [emp.to_dict() for emp in self.get_top_performers()],
            'problematic_employees': [emp.to_dict() for emp in self.get_problematic_employees()],
            'low_performers': [emp.to_dict() for emp in self.get_low_performers()]
        }

    def __str__(self) -> str:
        """String representation"""
        return (f"AnalysisResult({self.start_date} to {self.end_date}) "
                f"{self.total_estates} estates, {self.total_divisions} divisions, "
                f"{self.grand_kerani} Kerani ({self.grand_verification_rate:.1f}% verified)")

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"AnalysisResult(start_date={self.start_date}, end_date={self.end_date}, "
                f"estates={self.total_estates}, divisions={self.total_divisions}, "
                f"grand_verification_rate={self.grand_verification_rate:.2f})")