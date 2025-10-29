#!/usr/bin/env python3
"""
Core Analysis Engine for FFB Scanner System
Handles all business logic for transaction analysis and verification.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date
from ..core.database import DatabaseManager


class FFBAnalyzer:
    """
    Main analysis engine for FFB transaction verification and performance analysis.
    Processes scanner data to detect verification rates and data quality issues.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize FFB analyzer with database manager.

        Args:
            db_manager: DatabaseManager instance for estate connections
        """
        self.db_manager = db_manager

    def analyze_estate(self, estate_name: str, start_date: date, end_date: date,
                      use_status_704_filter: bool = False) -> Optional[Dict]:
        """
        Analyze all divisions in an estate for specified date range.

        Args:
            estate_name: Name of the estate to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            use_status_704_filter: Special filter for May 2025 data

        Returns:
            Dictionary with analysis results or None if no data
        """
        print(f"Analyzing estate: {estate_name}")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Status 704 filter: {use_status_704_filter}")

        # Get estate data
        divisions, month_tables = self.db_manager.get_divisions(estate_name, start_date, end_date)

        if not divisions:
            print(f"No divisions found for {estate_name}")
            return None

        employee_mapping = self.db_manager.get_employee_mapping(estate_name)

        if use_status_704_filter:
            print(f"*** FILTER TRANSSTATUS 704 AKTIF untuk {estate_name} ***")
            print(f"Menggunakan analisis transaksi real (bukan nilai statis)")

        # Analyze each division
        estate_results = []
        estate_employee_totals = {}

        for div_id, div_name in divisions.items():
            print(f"\nAnalyzing division: {div_name} (ID: {div_id})")

            # Get transaction data for this division
            transaction_data = self.db_manager.get_transaction_data(
                estate_name, div_id, start_date, end_date, month_tables
            )

            if transaction_data.empty:
                print(f"No transaction data found for division {div_name}")
                continue

            # Analyze division
            division_result = self._analyze_division(
                estate_name, div_id, div_name, transaction_data,
                employee_mapping, use_status_704_filter
            )

            if division_result:
                # Accumulate employee totals across divisions
                for emp_id, emp_data in division_result['employee_details'].items():
                    if emp_id not in estate_employee_totals:
                        estate_employee_totals[emp_id] = {
                            'name': emp_data['name'],
                            'kerani': 0,
                            'kerani_verified': 0,
                            'kerani_differences': 0,
                            'mandor': 0,
                            'asisten': 0
                        }

                    # Add to estate totals
                    estate_employee_totals[emp_id]['kerani'] += emp_data['kerani']
                    estate_employee_totals[emp_id]['kerani_verified'] += emp_data['kerani_verified']
                    estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
                    estate_employee_totals[emp_id]['mandor'] += emp_data['mandor']
                    estate_employee_totals[emp_id]['asisten'] += emp_data['asisten']

                estate_results.append(division_result)

        if use_status_704_filter and estate_employee_totals:
            total_actual_differences = sum(
                emp_data['kerani_differences'] for emp_data in estate_employee_totals.values()
            )
            print(f"HASIL ANALISIS REAL: {total_actual_differences} total perbedaan ditemukan")

            # Log detail per karyawan untuk transparansi
            for emp_id, emp_data in estate_employee_totals.items():
                if emp_data['kerani_differences'] > 0:
                    user_name = emp_data['name']
                    differences = emp_data['kerani_differences']
                    verified = emp_data['kerani_verified']
                    percentage = (differences / verified * 100) if verified > 0 else 0
                    print(f"  {user_name}: {differences} perbedaan dari {verified} transaksi terverifikasi ({percentage:.1f}%)")

        # Update division results with estate totals
        for result in estate_results:
            result['estate_employee_totals'] = estate_employee_totals

        return {
            'estate': estate_name,
            'start_date': start_date,
            'end_date': end_date,
            'divisions': estate_results,
            'estate_employee_totals': estate_employee_totals,
            'use_status_704_filter': use_status_704_filter
        }

    def _analyze_division(self, estate_name: str, div_id: str, div_name: str,
                       transaction_data: pd.DataFrame, employee_mapping: Dict[str, str],
                       use_status_704_filter: bool) -> Optional[Dict]:
        """
        Analyze a single division's transaction data.

        Args:
            estate_name: Estate name
            div_id: Division ID
            div_name: Division name
            transaction_data: DataFrame with transaction records
            employee_mapping: Employee ID to name mapping
            use_status_704_filter: Special filter flag

        Returns:
            Dictionary with division analysis results
        """
        if transaction_data.empty:
            return None

        print(f"  Processing {len(transaction_data)} transaction records")

        # Find duplicates based on TRANSNO
        duplicated_rows = transaction_data[transaction_data.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())

        print(f"  Found {len(verified_transnos)} verified transactions")

        # Initialize employee details
        employee_details = {}
        all_user_ids = transaction_data['SCANUSERID'].unique()

        for user_id in all_user_ids:
            user_id_str = str(user_id).strip()
            employee_details[user_id_str] = {
                'name': employee_mapping.get(user_id_str, f"EMP-{user_id_str}"),
                'kerani': 0,
                'kerani_verified': 0,
                'kerani_differences': 0,
                'mandor': 0,
                'asisten': 0
            }

        # Analyze Kerani data (RECORDTAG = 'PM')
        kerani_df = transaction_data[transaction_data['RECORDTAG'] == 'PM']
        if not kerani_df.empty:
            print(f"  Processing {len(kerani_df)} Kerani records")

            for user_id, group in kerani_df.groupby('SCANUSERID'):
                user_id_str = str(user_id).strip()
                total_created = len(group)

                # Count differences for verified transactions
                differences_count = 0
                for _, kerani_row in group.iterrows():
                    if kerani_row['TRANSNO'] in verified_transnos:
                        # Find matching transactions with different RECORDTAG
                        matching_transactions = transaction_data[
                            (transaction_data['TRANSNO'] == kerani_row['TRANSNO']) &
                            (transaction_data['RECORDTAG'] != 'PM')
                        ]

                        # Apply status 704 filter for May 2025
                        if use_status_704_filter:
                            matching_transactions = matching_transactions[
                                matching_transactions['TRANSSTATUS'] == '704'
                            ]

                        if not matching_transactions.empty:
                            # Prioritize P1 (Asisten) over P5 (Mandor)
                            p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                            p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']

                            if not p1_records.empty:
                                other_row = p1_records.iloc[0]
                            elif not p5_records.empty:
                                other_row = p5_records.iloc[0]
                            else:
                                continue

                            # Compare fields for differences
                            if self._has_transaction_differences(kerani_row, other_row):
                                differences_count += 1

                # Calculate verification metrics
                verified_count = len(group[group['TRANSNO'].isin(verified_transnos)])
                verification_rate = (verified_count / total_created * 100) if total_created > 0 else 0

                # Update employee details
                if user_id_str in employee_details:
                    employee_details[user_id_str]['kerani'] = total_created
                    employee_details[user_id_str]['kerani_verified'] = verified_count
                    employee_details[user_id_str]['kerani_differences'] = differences_count

                print(f"    {user_id_str}: {total_created} created, {verified_count} verified, {differences_count} differences")

        # Analyze Mandor data (RECORDTAG = 'P1')
        mandor_df = transaction_data[transaction_data['RECORDTAG'] == 'P1']
        if not mandor_df.empty:
            print(f"  Processing {len(mandor_df)} Mandor records")
            for user_id, count in mandor_df.groupby('SCANUSERID').size().items():
                user_id_str = str(user_id).strip()
                if user_id_str in employee_details:
                    employee_details[user_id_str]['mandor'] = count

        # Analyze Asisten data (RECORDTAG = 'P5')
        asisten_df = transaction_data[transaction_data['RECORDTAG'] == 'P5']
        if not asisten_df.empty:
            print(f"  Processing {len(asisten_df)} Asisten records")
            for user_id, count in asisten_df.groupby('SCANUSERID').size().items():
                user_id_str = str(user_id).strip()
                if user_id_str in employee_details:
                    employee_details[user_id_str]['asisten'] = count

        # Calculate division totals
        kerani_total = sum(d['kerani'] for d in employee_details.values())
        mandor_total = sum(d['mandor'] for d in employee_details.values())
        asisten_total = sum(d['asisten'] for d in employee_details.values())

        # Calculate overall verification rate
        total_verified = sum(d['kerani_verified'] for d in employee_details.values())
        verification_rate = (total_verified / kerani_total * 100) if kerani_total > 0 else 0

        # Log summary for division
        print(f"  Division Summary:")
        print(f"    Kerani Total: {kerani_total}")
        print(f"    Mandor Total: {mandor_total}")
        print(f"    Asisten Total: {asisten_total}")
        print(f"    Verification Rate: {verification_rate:.2f}%")

        if use_status_704_filter:
            total_differences = sum(d['kerani_differences'] for d in employee_details.values())
            print(f"    Total Differences (704 filter): {total_differences}")

        return {
            'estate': estate_name,
            'division': div_name,
            'division_id': div_id,
            'kerani_total': kerani_total,
            'mandor_total': mandor_total,
            'asisten_total': asisten_total,
            'verifikasi_total': total_verified,
            'verification_rate': verification_rate,
            'employee_details': employee_details,
            'total_transactions': len(transaction_data),
            'verified_transactions': len(verified_transnos),
            'use_status_704_filter': use_status_704_filter
        }

    def _has_transaction_differences(self, kerani_row, other_row) -> bool:
        """
        Check if there are differences between Kerani and other role transactions.

        Args:
            kerani_row: Kerani transaction data
            other_row: Other role (Mandor/Asisten) transaction data

        Returns:
            True if there are field differences, False otherwise
        """
        fields_to_compare = [
            'RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH',
            'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT'
        ]

        for field in fields_to_compare:
            try:
                kerani_val = self._safe_float_convert(kerani_row[field])
                other_val = self._safe_float_convert(other_row[field])

                if kerani_val != other_val:
                    return True  # Found difference
            except (ValueError, TypeError) as e:
                print(f"Warning: Error comparing {field}: {e}")
                continue

        return False  # No differences found

    def _safe_float_convert(self, value) -> float:
        """
        Safely convert a value to float for comparison.

        Args:
            value: Value to convert

        Returns:
            Float value or 0 if conversion fails
        """
        try:
            if pd.isna(value) or value is None or value == '':
                return 0.0
            return float(str(value).strip())
        except (ValueError, TypeError):
            return 0.0

    def analyze_multiple_estates(self, estate_names: List[str], start_date: date, end_date: date,
                             use_status_704_filter: bool = False) -> Dict:
        """
        Analyze multiple estates for the specified date range.

        Args:
            estate_names: List of estate names to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            use_status_704_filter: Special filter for May 2025 data

        Returns:
            Dictionary with multi-estate analysis results
        """
        print(f"\n{'='*80}")
        print(f"MULTI-ESTATE ANALYSIS")
        print(f"Estates: {', '.join(estate_names)}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Status 704 Filter: {use_status_704_filter}")
        print(f"{'='*80}")

        results = {}
        grand_totals = {
            'kerani_total': 0,
            'mandor_total': 0,
            'asisten_total': 0,
            'verifikasi_total': 0,
            'kerani_differences': 0,
            'total_divisions': 0,
            'successful_estates': 0
        }

        for estate_name in estate_names:
            print(f"\n{'-'*60}")
            print(f"PROCESSING: {estate_name}")
            print(f"{'-'*60}")

            estate_result = self.analyze_estate(
                estate_name, start_date, end_date, use_status_704_filter
            )

            if estate_result:
                results[estate_name] = estate_result
                grand_totals['successful_estates'] += 1
                grand_totals['total_divisions'] += len(estate_result['divisions'])
                grand_totals['kerani_total'] += estate_result.get('total_kerani', 0)
                grand_totals['mandor_total'] += estate_result.get('total_mandor', 0)
                grand_totals['asisten_total'] += estate_result.get('total_asisten', 0)
                grand_totals['verifikasi_total'] += estate_result.get('total_verified', 0)
                grand_totals['kerani_differences'] += estate_result.get('total_differences', 0)
            else:
                results[estate_name] = {
                    'estate': estate_name,
                    'status': 'failed',
                    'message': 'No data available'
                }

        # Calculate grand totals
        grand_verification_rate = (
            grand_totals['verifikasi_total'] / grand_totals['kerani_total'] * 100
        ) if grand_totals['kerani_total'] > 0 else 0

        results['_summary'] = {
            'estates_analyzed': len(estate_names),
            'successful_estates': grand_totals['successful_estates'],
            'total_divisions': grand_totals['total_divisions'],
            'kerani_total': grand_totals['kerani_total'],
            'mandor_total': grand_totals['mandor_total'],
            'asisten_total': grand_totals['asisten_total'],
            'verifikasi_total': grand_totals['verifikasi_total'],
            'verification_rate': grand_verification_rate,
            'kerani_differences': grand_totals['kerani_differences'],
            'use_status_704_filter': use_status_704_filter
        }

        print(f"\n{'='*80}")
        print(f"MULTI-ESTATE ANALYSIS COMPLETE")
        print(f"Estates Processed: {grand_totals['successful_estates']}/{len(estate_names)}")
        print(f"Total Divisions: {grand_totals['total_divisions']}")
        print(f"Grand Verification Rate: {grand_verification_rate:.2f}%")
        print(f"Total Kerani Differences: {grand_totals['kerani_differences']}")
        print(f"{'='*80}")

        return results

    def get_estate_summary(self, estate_result: Dict) -> Dict:
        """
        Calculate summary statistics for a single estate result.

        Args:
            estate_result: Result dictionary from analyze_estate

        Returns:
            Dictionary with summary statistics
        """
        if not estate_result or 'divisions' not in estate_result:
            return {}

        divisions = estate_result['divisions']
        if not divisions:
            return {}

        summary = {
            'total_divisions': len(divisions),
            'total_kerani': sum(div.get('kerani_total', 0) for div in divisions),
            'total_mandor': sum(div.get('mandor_total', 0) for div in divisions),
            'total_asisten': sum(div.get('asisten_total', 0) for div in divisions),
            'total_verified': sum(div.get('verifikasi_total', 0) for div in divisions),
            'total_differences': sum(
                emp_data.get('kerani_differences', 0)
                for div in divisions
                for emp_data in div.get('employee_details', {}).values()
            ),
            'use_status_704_filter': estate_result.get('use_status_704_filter', False)
        }

        # Calculate verification rate
        if summary['total_kerani'] > 0:
            summary['verification_rate'] = (
                summary['total_verified'] / summary['total_kerani'] * 100
            )
        else:
            summary['verification_rate'] = 0

        return summary


class AnalysisValidator:
    """
    Validates analysis results and ensures data consistency.
    """

    @staticmethod
    def validate_estate_result(estate_result: Dict) -> Tuple[bool, List[str]]:
        """
        Validate analysis result for a single estate.

        Args:
            estate_result: Estate analysis result to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if not estate_result:
            issues.append("Empty estate result")
            return False, issues

        required_fields = [
            'estate', 'divisions', 'estate_employee_totals',
            'start_date', 'end_date'
        ]

        for field in required_fields:
            if field not in estate_result:
                issues.append(f"Missing required field: {field}")

        # Validate divisions
        divisions = estate_result.get('divisions', [])
        if not isinstance(divisions, list):
            issues.append("Divisions should be a list")

        for i, division in enumerate(divisions):
            if not isinstance(division, dict):
                issues.append(f"Division {i} should be a dictionary")

            div_required_fields = [
                'division', 'kerani_total', 'mandor_total',
                'asisten_total', 'employee_details'
            ]

            for field in div_required_fields:
                if field not in division:
                    issues.append(f"Division {i} missing field: {field}")

        # Validate employee details
        employee_totals = estate_result.get('estate_employee_totals', {})
        if not isinstance(employee_totals, dict):
            issues.append("Employee totals should be a dictionary")

        return len(issues) == 0, issues

    @staticmethod
    def validate_multi_estate_results(results: Dict) -> Tuple[bool, List[str]]:
        """
        Validate multi-estate analysis results.

        Args:
            results: Multi-estate analysis results

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if not isinstance(results, dict):
            issues.append("Results should be a dictionary")

        if '_summary' not in results:
            issues.append("Missing summary in results")

        summary = results.get('_summary', {})
        summary_required_fields = [
            'estates_analyzed', 'successful_estates',
            'total_divisions', 'kerani_total', 'verification_rate'
        ]

        for field in summary_required_fields:
            if field not in summary:
                issues.append(f"Summary missing field: {field}")

        # Validate individual estate results
        for estate_name, estate_result in results.items():
            if estate_name.startswith('_'):  # Skip summary keys
                continue

            is_valid, estate_issues = AnalysisValidator.validate_estate_result(estate_result)
            if not is_valid:
                issues.extend([f"Estate {estate_name}: {issue}" for issue in estate_issues])

        return len(issues) == 0, issues