"""
Excel Exporter
Excel report generation for FFB Analysis System
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics


class ExcelExporter:
    """
    Excel report generator for FFB analysis results
    """

    def __init__(self):
        """Initialize Excel exporter"""
        self.writer = None
        self.output_file = None

    def create_detailed_report(self, analysis_result: AnalysisResult,
                            output_path: str) -> str:
        """
        Create detailed Excel report with multiple worksheets

        :param analysis_result: Analysis result data
        :param output_path: Output Excel file path
        :return: Path to generated Excel file
        """
        try:
            # Create Excel writer
            self.output_file = output_path
            self.writer = pd.ExcelWriter(output_path, engine='openpyxl')

            # Create worksheets
            self._create_summary_sheet(analysis_result)
            self._create_grand_totals_sheet(analysis_result)
            self._create_estate_breakdown_sheet(analysis_result)
            self._create_division_details_sheet(analysis_result)
            self._create_employee_details_sheet(analysis_result)
            self._create_top_performers_sheet(analysis_result)
            self._create_quality_issues_sheet(analysis_result)

            # Save and close
            self.writer.close()
            return output_path

        except Exception as e:
            print(f"Error creating Excel report: {e}")
            raise

    def _create_summary_sheet(self, analysis_result: AnalysisResult):
        """Create summary worksheet"""
        summary_data = []

        # Analysis metadata
        summary = analysis_result.get_analysis_summary()
        summary_data.extend([
            ['ANALYSIS SUMMARY', '', ''],
            ['Analysis Date', summary['analysis_date'], ''],
            ['Period Start', summary['period']['start_date'], ''],
            ['Period End', summary['period']['end_date'], ''],
            ['Period Days', summary['period']['days'], ''],
            ['Analysis Version', summary['metadata']['analysis_version'], ''],
            ['Duration (seconds)', summary['metadata']['analysis_duration_seconds'], ''],
            ['Use Status 704 Filter', summary['metadata']['use_status_704_filter'], ''],
            ['', '', ''],
            ['ESTATES SUMMARY', '', ''],
            ['Estates Analyzed', len(summary['estates']['analyzed']), ''],
            ['Active Estates', summary['estates']['active_count'], ''],
            ['', '', ''],
            ['GRAND TOTALS', '', ''],
            ['Total Kerani Transactions', summary['grand_totals']['kerani'], ''],
            ['Total Mandor Transactions', summary['grand_totals']['mandor'], ''],
            ['Total Asisten Transactions', summary['grand_totals']['asisten'], ''],
            ['Total Verified Transactions', summary['grand_totals']['verified'], ''],
            ['Total Differences', summary['grand_totals']['differences'], ''],
            ['Overall Verification Rate (%)', summary['grand_totals']['verification_rate'], ''],
            ['Overall Difference Rate (%)', summary['grand_totals']['difference_rate'], ''],
        ])

        df_summary = pd.DataFrame(summary_data, columns=['Metric', 'Value', 'Notes'])
        df_summary.to_excel(self.writer, sheet_name='Summary', index=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Summary']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 15

    def _create_grand_totals_sheet(self, analysis_result: AnalysisResult):
        """Create grand totals worksheet"""
        totals_data = []

        # Header
        totals_data.append(['GRAND TOTALS - ALL ESTATES', '', '', '', '', '', ''])

        # Estate names row
        estate_names = analysis_result.analyzed_estates
        totals_data.append(['Estates:'] + estate_names + ['TOTAL'])

        # Blank row
        totals_data.append(['', '', '', '', '', '', ''])

        # Metrics rows
        totals_data.append(['Total Divisions'] + [''] * len(estate_names) + [analysis_result.total_divisions])
        totals_data.append(['Kerani Transactions'] + [''] * len(estate_names) + [analysis_result.grand_kerani])
        totals_data.append(['Mandor Transactions'] + [''] * len(estate_names) + [analysis_result.grand_mandor])
        totals_data.append(['Asisten Transactions'] + [''] * len(estate_names) + [analysis_result.grand_asisten])
        totals_data.append(['Verified Transactions'] + [''] * len(estate_names) + [analysis_result.grand_kerani_verified])
        totals_data.append(['Differences'] + [''] * len(estate_names) + [analysis_result.grand_differences])
        totals_data.append(['Verification Rate (%)'] + [''] * len(estate_names) + [analysis_result.grand_verification_rate])
        totals_data.append(['Difference Rate (%)'] + [''] * len(estate_names) + [analysis_result.grand_difference_rate])

        # Add estate-specific data
        estate_summaries = analysis_result.get_estate_summaries()
        if estate_summaries:
            # Create mapping of estate to column
            estate_columns = {estate: i+1 for i, estate in enumerate(estate_names)}

            for estate_name, divisions in estate_summaries.items():
                if estate_name in estate_columns:
                    col = estate_columns[estate_name]
                    estate_totals = self._calculate_estate_totals(divisions)

                    # Update the rows
                    for i, row in enumerate(totals_data):
                        if i == 3:  # Total Divisions
                            row[col] = len(divisions)
                        elif i == 4:  # Kerani Transactions
                            row[col] = estate_totals['kerani']
                        elif i == 5:  # Mandor Transactions
                            row[col] = estate_totals['mandor']
                        elif i == 6:  # Asisten Transactions
                            row[col] = estate_totals['asisten']
                        elif i == 7:  # Verified Transactions
                            row[col] = estate_totals['verified']
                        elif i == 8:  # Differences
                            row[col] = estate_totals['differences']
                        elif i == 9:  # Verification Rate
                            row[col] = estate_totals['verification_rate']
                        elif i == 10:  # Difference Rate
                            row[col] = estate_totals['difference_rate']

        df_totals = pd.DataFrame(totals_data)
        df_totals.to_excel(self.writer, sheet_name='Grand Totals', index=False, header=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Grand Totals']
        worksheet.column_dimensions['A'].width = 25
        for i in range(1, min(len(estate_names) + 2, 20)):
            worksheet.column_dimensions[chr(64 + i)].width = 15

    def _calculate_estate_totals(self, divisions: List[DivisionSummary]) -> Dict[str, Any]:
        """Calculate totals for an estate"""
        return {
            'divisions': len(divisions),
            'kerani': sum(d.kerani_total for d in divisions),
            'mandor': sum(d.mandor_total for d in divisions),
            'asisten': sum(d.asisten_total for d in divisions),
            'verified': sum(d.verification_total for d in divisions),
            'differences': sum(d.difference_count for d in divisions),
            'verification_rate': (sum(d.verification_total for d in divisions) /
                               sum(d.kerani_total for d in divisions) * 100) if sum(d.kerani_total for d in divisions) > 0 else 0,
            'difference_rate': (sum(d.difference_count for d in divisions) /
                             sum(d.verification_total for d in divisions) * 100) if sum(d.verification_total for d in divisions) > 0 else 0
        }

    def _create_estate_breakdown_sheet(self, analysis_result: AnalysisResult):
        """Create estate breakdown worksheet"""
        breakdown_data = []

        # Header
        breakdown_data.append([
            'Estate', 'Division', 'Division ID', 'Kerani Transactions',
            'Mandor Transactions', 'Asisten Transactions', 'Verified Transactions',
            'Verification Rate (%)', 'Differences', 'Difference Rate (%)', 'Employee Count'
        ])

        # Add data for each division
        for division_summary in analysis_result.get_division_summaries():
            breakdown_data.append([
                division_summary.estate_name,
                division_summary.division_name,
                division_summary.division_id,
                division_summary.kerani_total,
                division_summary.mandor_total,
                division_summary.asisten_total,
                division_summary.verification_total,
                round(division_summary.verification_rate, 2),
                division_summary.difference_count,
                round(division_summary.difference_rate, 2),
                division_summary.employee_count
            ])

        df_breakdown = pd.DataFrame(breakdown_data)
        df_breakdown.to_excel(self.writer, sheet_name='Estate Breakdown', index=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Estate Breakdown']
        column_widths = {
            'A': 15, 'B': 20, 'C': 12, 'D': 18, 'E': 18, 'F': 18,
            'G': 18, 'H': 16, 'I': 12, 'J': 16, 'K': 12
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

    def _create_division_details_sheet(self, analysis_result: AnalysisResult):
        """Create detailed division analysis worksheet"""
        details_data = []

        # Header
        details_data.append([
            'Estate', 'Division', 'Employee ID', 'Employee Name', 'Role',
            'Kerani Transactions', 'Kerani Verified', 'Kerani Differences',
            'Mandor Transactions', 'Asisten Transactions',
            'Verification Rate (%)', 'Difference Rate (%)'
        ])

        # Add detailed employee data
        for division_summary in analysis_result.get_division_summaries():
            for emp_metrics in division_summary.get_employee_metrics():
                details_data.append([
                    emp_metrics.estate,
                    emp_metrics.division,
                    emp_metrics.employee_id,
                    emp_metrics.employee_name,
                    self._get_employee_role(emp_metrics),
                    emp_metrics.kerani_transactions,
                    emp_metrics.kerani_verified,
                    emp_metrics.kerani_differences,
                    emp_metrics.mandor_transactions,
                    emp_metrics.asisten_transactions,
                    round(emp_metrics.verification_rate, 2),
                    round(emp_metrics.difference_rate, 2)
                ])

        df_details = pd.DataFrame(details_data)
        df_details.to_excel(self.writer, sheet_name='Division Details', index=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Division Details']
        column_widths = {
            'A': 15, 'B': 20, 'C': 12, 'D': 25, 'E': 10, 'F': 16,
            'G': 16, 'H': 16, 'I': 16, 'J': 16, 'K': 16, 'L': 16
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

    def _get_employee_role(self, emp_metrics: EmployeeMetrics) -> str:
        """Get employee role string"""
        if emp_metrics.kerani_transactions > 0:
            return 'Kerani'
        elif emp_metrics.mandor_transactions > 0:
            return 'Mandor'
        elif emp_metrics.asisten_transactions > 0:
            return 'Asisten'
        else:
            return 'Unknown'

    def _create_employee_details_sheet(self, analysis_result: AnalysisResult):
        """Create employee-focused worksheet"""
        employee_data = []

        # Header
        employee_data.append([
            'Employee ID', 'Employee Name', 'Estate', 'Division', 'Primary Role',
            'Total Kerani', 'Verified Kerani', 'Kerani Differences',
            'Total Mandor', 'Total Asisten', 'Total Transactions',
            'Verification Rate (%)', 'Difference Rate (%)', 'Performance Score'
        ])

        # Get all unique employees
        all_employees = analysis_result.get_all_employee_metrics()
        employee_dict = {}

        # Deduplicate employees (they might appear in multiple divisions)
        for emp in all_employees:
            key = (emp.employee_id, emp.employee_name)
            if key not in employee_dict:
                employee_dict[key] = {
                    'id': emp.employee_id,
                    'name': emp.employee_name,
                    'estates': set(),
                    'divisions': set(),
                    'kerani_total': 0,
                    'kerani_verified': 0,
                    'kerani_differences': 0,
                    'mandor_total': 0,
                    'asisten_total': 0
                }

            emp_data = employee_dict[key]
            emp_data['estates'].add(emp.estate)
            emp_data['divisions'].add(emp.division)
            emp_data['kerani_total'] += emp.kerani_transactions
            emp_data['kerani_verified'] += emp.kerani_verified
            emp_data['kerani_differences'] += emp.kerani_differences
            emp_data['mandor_total'] += emp.mandor_transactions
            emp_data['asisten_total'] += emp.asisten_transactions

        # Create final employee data
        for emp_key, emp_data in employee_dict.items():
            verification_rate = (emp_data['kerani_verified'] / emp_data['kerani_total'] * 100) if emp_data['kerani_total'] > 0 else 0
            difference_rate = (emp_data['kerani_differences'] / emp_data['kerani_verified'] * 100) if emp_data['kerani_verified'] > 0 else 0
            total_transactions = emp_data['kerani_total'] + emp_data['mandor_total'] + emp_data['asisten_total']

            # Calculate performance score (0-100)
            performance_score = min(100, verification_rate - (difference_rate * 0.5))

            employee_data.append([
                emp_data['id'],
                emp_data['name'],
                ', '.join(sorted(emp_data['estates'])),
                ', '.join(sorted(emp_data['divisions'])),
                'Kerani' if emp_data['kerani_total'] > 0 else ('Mandor' if emp_data['mandor_total'] > 0 else 'Asisten'),
                emp_data['kerani_total'],
                emp_data['kerani_verified'],
                emp_data['kerani_differences'],
                emp_data['mandor_total'],
                emp_data['asisten_total'],
                total_transactions,
                round(verification_rate, 2),
                round(difference_rate, 2),
                round(performance_score, 2)
            ])

        df_employees = pd.DataFrame(employee_data)
        df_employees.to_excel(self.writer, sheet_name='Employee Details', index=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Employee Details']
        column_widths = {
            'A': 12, 'B': 25, 'C': 20, 'D': 25, 'E': 12, 'F': 12,
            'G': 12, 'H': 12, 'I': 12, 'J': 12, 'K': 12, 'L': 16, 'M': 16, 'N': 12
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

    def _create_top_performers_sheet(self, analysis_result: AnalysisResult):
        """Create top performers worksheet"""
        performers_data = []

        # Header
        performers_data.append([
            'Rank', 'Employee ID', 'Employee Name', 'Estate', 'Division',
            'Kerani Transactions', 'Verified Transactions', 'Verification Rate (%)',
            'Differences', 'Difference Rate (%)', 'Performance Grade'
        ])

        # Get top performers
        top_performers = analysis_result.get_top_performers(50)  # Top 50

        for rank, emp in enumerate(top_performers, 1):
            grade = self._calculate_performance_grade(emp.verification_rate, emp.difference_rate)

            performers_data.append([
                rank,
                emp.employee_id,
                emp.employee_name,
                emp.estate,
                emp.division,
                emp.kerani_transactions,
                emp.kerani_verified,
                round(emp.verification_rate, 2),
                emp.kerani_differences,
                round(emp.difference_rate, 2),
                grade
            ])

        df_performers = pd.DataFrame(performers_data)
        df_performers.to_excel(self.writer, sheet_name='Top Performers', index=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Top Performers']
        column_widths = {
            'A': 8, 'B': 12, 'C': 25, 'D': 15, 'E': 20, 'F': 16,
            'G': 16, 'H': 16, 'I': 12, 'J': 16, 'K': 16
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

    def _create_quality_issues_sheet(self, analysis_result: AnalysisResult):
        """Create quality issues worksheet"""
        if analysis_result.grand_differences == 0:
            # Create empty sheet with message
            empty_data = [['Quality Issues', ''], ['No quality issues found in this analysis period', '']]
            df_empty = pd.DataFrame(empty_data)
            df_empty.to_excel(self.writer, sheet_name='Quality Issues', index=False, header=False)
            return

        issues_data = []

        # Header
        issues_data.append([
            'Employee ID', 'Employee Name', 'Estate', 'Division',
            'Kerani Transactions', 'Verified Transactions', 'Differences',
            'Difference Rate (%)', 'Severity Level', 'Recommended Action'
        ])

        # Get problematic employees
        problematic = analysis_result.get_problematic_employees(100)  # Top 100

        for emp in problematic:
            severity = self._calculate_severity_level(emp.difference_rate)
            action = self._get_recommended_action(emp.difference_rate)

            issues_data.append([
                emp.employee_id,
                emp.employee_name,
                emp.estate,
                emp.division,
                emp.kerani_transactions,
                emp.kerani_verified,
                emp.kerani_differences,
                round(emp.difference_rate, 2),
                severity,
                action
            ])

        df_issues = pd.DataFrame(issues_data)
        df_issues.to_excel(self.writer, sheet_name='Quality Issues', index=False)

        # Adjust column widths
        worksheet = self.writer.sheets['Quality Issues']
        column_widths = {
            'A': 12, 'B': 25, 'C': 15, 'D': 20, 'E': 16, 'F': 16,
            'G': 12, 'H': 16, 'I': 12, 'J': 20
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

    def _calculate_performance_grade(self, verification_rate: float, difference_rate: float) -> str:
        """Calculate performance grade"""
        score = verification_rate - (difference_rate * 0.5)

        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _calculate_severity_level(self, difference_rate: float) -> str:
        """Calculate severity level for quality issues"""
        if difference_rate >= 20:
            return 'Critical'
        elif difference_rate >= 10:
            return 'High'
        elif difference_rate >= 5:
            return 'Medium'
        else:
            return 'Low'

    def _get_recommended_action(self, difference_rate: float) -> str:
        """Get recommended action based on difference rate"""
        if difference_rate >= 20:
            return 'Immediate training required'
        elif difference_rate >= 10:
            return 'Additional supervision needed'
        elif difference_rate >= 5:
            return 'Review data entry process'
        else:
            return 'Monitor performance'

    def create_summary_excel(self, analysis_result: AnalysisResult,
                           output_path: str) -> str:
        """
        Create simplified Excel report with key metrics only

        :param analysis_result: Analysis result data
        :param output_path: Output Excel file path
        :return: Path to generated Excel file
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Summary only
                self._create_summary_sheet(analysis_result)

                # Top performers (top 10)
                top_performers = analysis_result.get_top_performers(10)
                performers_data = []

                performers_data.append(['Rank', 'Employee Name', 'Estate', 'Verification Rate (%)'])
                for rank, emp in enumerate(top_performers, 1):
                    performers_data.append([
                        rank, emp.employee_name, emp.estate, round(emp.verification_rate, 2)
                    ])

                df_performers = pd.DataFrame(performers_data)
                df_performers.to_excel(writer, sheet_name='Top Performers', index=False)

            return output_path

        except Exception as e:
            print(f"Error creating summary Excel: {e}")
            raise