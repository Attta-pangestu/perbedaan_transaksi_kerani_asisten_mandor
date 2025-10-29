"""
Analysis Service
Core business logic for FFB transaction analysis
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple
from models.transaction import Transaction, TransactionGroup
from models.employee import Employee, EmployeeManager
from models.division import Division, DivisionManager
from models.estate import Estate, EstateManager
from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics
from repositories.database_repository import DatabaseRepository
from repositories.transaction_repository import TransactionRepository
from repositories.employee_repository import EmployeeRepository
from repositories.division_repository import DivisionRepository


class AnalysisService:
    """
    Core service for FFB transaction analysis
    """

    def __init__(self, config_service=None):
        """
        Initialize analysis service

        :param config_service: Optional configuration service
        """
        self.config_service = config_service
        self._cache = {}

    def analyze_estate(self, estate_name: str, db_path: str,
                      start_date: date, end_date: date,
                      use_status_704_filter: bool = False) -> Optional[List[DivisionSummary]]:
        """
        Analyze a single estate

        :param estate_name: Name of the estate
        :param db_path: Database file path
        :param start_date: Analysis start date
        :param end_date: Analysis end date
        :param use_status_704_filter: Apply TRANSSTATUS 704 filter for May 2025
        :return: List of division summaries or None if error
        """
        try:
            # Create repositories
            db_repo = DatabaseRepository.create(db_path)
            if not db_repo.test_connection():
                print(f"Cannot connect to database: {db_path}")
                return None

            transaction_repo = TransactionRepository(db_repo.connector)
            employee_repo = EmployeeRepository(db_repo.connector)
            division_repo = DivisionRepository(db_repo.connector)

            # Get divisions with transactions
            divisions = division_repo.get_divisions_with_transactions(
                transaction_repo, start_date, end_date
            )

            if not divisions:
                print(f"No divisions found with transactions for {estate_name}")
                return []

            # Analyze each division
            division_summaries = []
            for division in divisions:
                summary = self.analyze_division(
                    estate_name, division, transaction_repo,
                    employee_repo, start_date, end_date, use_status_704_filter
                )
                if summary:
                    division_summaries.append(summary)

            return division_summaries

        except Exception as e:
            print(f"Error analyzing estate {estate_name}: {e}")
            return None

    def analyze_division(self, estate_name: str, division: Division,
                         transaction_repo: TransactionRepository,
                         employee_repo: EmployeeRepository,
                         start_date: date, end_date: date,
                         use_status_704_filter: bool = False) -> Optional[DivisionSummary]:
        """
        Analyze a single division

        :param estate_name: Estate name
        :param division: Division object
        :param transaction_repo: Transaction repository
        :param employee_repo: Employee repository
        :param start_date: Start date
        :param end_date: End date
        :param use_status_704_filter: Apply status 704 filter
        :return: DivisionSummary or None if error
        """
        try:
            # Get transactions for this division
            transactions = transaction_repo.get_transactions_by_date_range(
                start_date, end_date, division.id
            )

            if not transactions:
                print(f"No transactions found for division {division.name}")
                return None

            # Get employee mapping
            employee_mapping = employee_repo.get_complete_employee_mapping()

            # Process transactions and calculate metrics
            employee_manager = self._process_transactions(
                transactions, employee_mapping, use_status_704_filter
            )

            # Set estate context for employees
            for employee in employee_manager.employees.values():
                employee.estate = estate_name
                employee.division = division.name

            # Update division with employee data
            for employee in employee_manager.get_active_employees():
                division.add_employee(employee)

            # Create division summary
            summary = DivisionSummary.from_division(division)

            print(f"Division {division.name}: {len(summary.get_employee_metrics())} employees, "
                  f"{summary.kerani_total} Kerani transactions ({summary.verification_rate:.1f}% verified)")

            # Log details for employees with differences
            problematic_employees = summary.get_problematic_employees()
            for emp in problematic_employees:
                print(f"  {emp.employee_name}: {emp.kerani_differences} differences from "
                      f"{emp.kerani_verified} verified ({emp.difference_rate:.1f}%)")

            return summary

        except Exception as e:
            print(f"Error analyzing division {division.name}: {e}")
            return None

    def _process_transactions(self, transactions: List[Transaction],
                             employee_mapping: Dict[str, str],
                             use_status_704_filter: bool = False) -> EmployeeManager:
        """
        Process transactions and calculate employee metrics

        :param transactions: List of transactions to process
        :param employee_mapping: Employee ID to name mapping
        :param use_status_704_filter: Apply status 704 filter
        :return: EmployeeManager with processed metrics
        """
        employee_manager = EmployeeManager()

        # Group transactions by TRANSNO to find verified transactions
        verified_transnos = set()
        for transaction in transactions:
            if transaction.is_kerani():
                # Find matching verifier transactions
                matching_transactions = [
                    t for t in transactions
                    if t.transno == transaction.transno and t.is_verifier()
                ]

                # Apply status filter if requested
                if use_status_704_filter:
                    matching_transactions = [
                        t for t in matching_transactions if t.has_special_status()
                    ]

                if matching_transactions:
                    verified_transnos.add(transaction.transno)

        # Initialize employees for all unique user IDs
        for transaction in transactions:
            user_id = transaction.scanuserid
            employee_name = employee_mapping.get(user_id, f"EMP-{user_id}")
            employee = employee_manager.get_or_create_employee(user_id, employee_name)

            # Set role based on transaction type
            if transaction.is_kerani():
                employee.role = employee.determine_role()

        # Process each transaction
        for transaction in transactions:
            user_id = transaction.scanuserid
            employee = employee_manager.get_employee(user_id)

            if not employee:
                continue

            # Count transactions by role
            if transaction.is_kerani():
                is_verified = transaction.transno in verified_transnos
                differences = 0

                if is_verified:
                    # Find differences with verifier
                    for other_trans in transactions:
                        if (other_trans.transno == transaction.transno and
                            other_trans.is_verifier()):
                            if use_status_704_filter:
                                if not other_trans.has_special_status():
                                    continue

                            if transaction.has_differences(other_trans):
                                differences = 1  # Count as 1 difference per transaction
                                break

                employee.add_kerani_metrics(1 if is_verified else 0, differences)

            elif transaction.is_mandor():
                employee.add_mandor_transaction()

            elif transaction.is_asisten():
                employee.add_asisten_transaction()

        return employee_manager

    def analyze_multiple_estates(self, estate_configs: List[Tuple[str, str]],
                                 start_date: date, end_date: date,
                                 use_status_704_filter: bool = False,
                                 progress_callback=None) -> AnalysisResult:
        """
        Analyze multiple estates

        :param estate_configs: List of (estate_name, db_path) tuples
        :param start_date: Start date
        :param end_date: End date
        :param use_status_704_filter: Apply status 704 filter
        :param progress_callback: Optional progress callback function
        :return: AnalysisResult with all estate data
        """
        start_time = datetime.now()
        estate_names = [config[0] for config in estate_configs]

        # Create analysis result
        result = AnalysisResult.create_empty(start_date, end_date, estate_names)
        result.use_status_704_filter = use_status_704_filter

        print(f"Starting analysis of {len(estate_configs)} estates")
        print(f"Period: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")
        if use_status_704_filter:
            print("*** TRANSSTATUS 704 FILTER ACTIVE ***")

        total_estates = len(estate_configs)
        successful_estates = 0

        for i, (estate_name, db_path) in enumerate(estate_configs):
            if progress_callback:
                progress_callback(i, total_estates, f"Analyzing {estate_name}...")

            try:
                print(f"\nAnalyzing {estate_name} ({i+1}/{total_estates})...")

                division_summaries = self.analyze_estate(
                    estate_name, db_path, start_date, end_date, use_status_704_filter
                )

                if division_summaries:
                    for summary in division_summaries:
                        result.add_division_summary(summary)
                    successful_estates += 1
                    print(f"{estate_name}: {len(division_summaries)} divisions analyzed")
                else:
                    print(f"{estate_name}: No data available")

            except Exception as e:
                print(f"Error analyzing {estate_name}: {e}")
                continue

        # Calculate analysis duration
        end_time = datetime.now()
        result.analysis_duration_seconds = (end_time - start_time).total_seconds()

        # Log final results
        print(f"\n=== ANALYSIS COMPLETE ===")
        print(f"Estates analyzed: {successful_estates}/{total_estates}")
        print(f"Total divisions: {result.total_divisions}")
        print(f"Total Kerani transactions: {result.grand_kerani}")
        print(f"Verified transactions: {result.grand_kerani_verified}")
        print(f"Overall verification rate: {result.grand_verification_rate:.2f}%")
        print(f"Total differences: {result.grand_differences}")
        print(f"Analysis duration: {result.analysis_duration_seconds:.1f} seconds")

        if progress_callback:
            progress_callback(total_estates, total_estates, "Analysis complete")

        return result

    def get_month_tables_for_period(self, start_date: date, end_date: date) -> List[str]:
        """
        Get list of month tables for date range

        :param start_date: Start date
        :param end_date: End date
        :return: List of month table names
        """
        month_tables = []
        current = start_date

        while current <= end_date:
            table_name = f"FFBSCANNERDATA{current.month:02d}"
            if table_name not in month_tables:
                month_tables.append(table_name)

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)

        return month_tables

    def should_use_status_704_filter(self, start_date: date, end_date: date) -> bool:
        """
        Determine if status 704 filter should be applied

        :param start_date: Start date
        :param end_date: End date
        :return: True if filter should be applied
        """
        # Apply filter if date range includes May 2025
        may_2025_start = date(2025, 5, 1)
        may_2025_end = date(2025, 5, 31)

        # Check if date ranges overlap
        return not (end_date < may_2025_start or start_date > may_2025_end)

    def validate_analysis_parameters(self, estate_configs: List[Tuple[str, str]],
                                    start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Validate analysis parameters

        :param estate_configs: List of estate configurations
        :param start_date: Start date
        :param end_date: End date
        :return: Validation result dictionary
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Validate date range
        if start_date > end_date:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Start date cannot be after end date")

        # Validate estate configurations
        if not estate_configs:
            validation_result['is_valid'] = False
            validation_result['errors'].append("No estates configured for analysis")

        # Check for duplicate estate names
        estate_names = [config[0] for config in estate_configs]
        if len(estate_names) != len(set(estate_names)):
            validation_result['is_valid'] = False
            validation_result['errors'].append("Duplicate estate names found")

        # Validate database paths
        for estate_name, db_path in estate_configs:
            if not db_path:
                validation_result['warnings'].append(f"Estate {estate_name} has no database path")
            elif not os.path.exists(db_path):
                validation_result['warnings'].append(f"Database path does not exist: {db_path}")

        return validation_result

    def get_analysis_summary(self, result: AnalysisResult) -> str:
        """
        Get formatted analysis summary

        :param result: AnalysisResult object
        :return: Formatted summary string
        """
        summary_lines = [
            f"FFB SCANNER ANALYSIS SUMMARY",
            f"Period: {result.start_date.strftime('%d %B %Y')} - {result.end_date.strftime('%d %B %Y')}",
            f"Estates: {len(result.analyzed_estates)}",
            f"Divisions: {result.total_divisions}",
            "",
            "TRANSACTION SUMMARY:",
            f"Kerani Transactions: {result.grand_kerani}",
            f"Mandor Transactions: {result.grand_mandor}",
            f"Asisten Transactions: {result.grand_asisten}",
            f"Verified Transactions: {result.grand_kerani_verified}",
            f"Verification Rate: {result.grand_verification_rate:.2f}%",
            f"Differences Found: {result.grand_differences}",
            f"Difference Rate: {result.grand_difference_rate:.2f}%",
        ]

        # Add top performers
        top_performers = result.get_top_performers(5)
        if top_performers:
            summary_lines.extend([
                "",
                "TOP PERFORMERS (by verification rate):"
            ])
            for i, emp in enumerate(top_performers, 1):
                summary_lines.append(
                    f"{i}. {emp.employee_name}: {emp.verification_rate:.1f}% "
                    f"({emp.kerani_verified}/{emp.kerani_transactions})"
                )

        # Add problematic employees
        problematic = result.get_problematic_employees(5)
        if problematic:
            summary_lines.extend([
                "",
                "QUALITY CONCERNS (employees with differences):"
            ])
            for i, emp in enumerate(problematic, 1):
                summary_lines.append(
                    f"{i}. {emp.employee_name}: {emp.kerani_differences} differences "
                    f"({emp.difference_rate:.1f}%)"
                )

        return "\n".join(summary_lines)