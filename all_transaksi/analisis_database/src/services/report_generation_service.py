"""
Report Generation Service
Handles PDF and Excel report generation
"""

import os
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from models.analysis_result import AnalysisResult, DivisionSummary, EmployeeMetrics
from infrastructure.reporting.pdf_generator import PDFReportGenerator
from infrastructure.reporting.template_compatible_generator import TemplateCompatiblePDFGenerator
from infrastructure.reporting.excel_exporter import ExcelExporter


class ReportGenerationService:
    """
    Service for generating various types of reports
    """

    def __init__(self, output_directory: str = "reports"):
        """
        Initialize report generation service

        :param output_directory: Directory for output files
        """
        self.output_directory = output_directory
        self.pdf_generator = PDFReportGenerator()
        self.template_generator = TemplateCompatiblePDFGenerator()
        self.excel_exporter = ExcelExporter()

        # Ensure output directory exists
        self._ensure_output_directory()

    def _ensure_output_directory(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory, exist_ok=True)

    def generate_comprehensive_pdf_report(self, analysis_result: AnalysisResult,
                                         include_charts: bool = True,
                                         include_details: bool = True) -> str:
        """
        Generate comprehensive PDF report

        :param analysis_result: Analysis result data
        :param include_charts: Whether to include charts
        :param include_details: Whether to include detailed breakdowns
        :return: Path to generated PDF file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            period_str = f"{analysis_result.start_date.strftime('%B_%Y')}"
            filename = f"Laporan_Kinerja_Komprehensif_{period_str}_{timestamp}.pdf"
            filepath = os.path.join(self.output_directory, filename)

            # Generate PDF report
            self.pdf_generator.create_comprehensive_report(
                analysis_result=analysis_result,
                output_path=filepath,
                include_charts=include_charts,
                include_details=include_details
            )

            return filepath

        except Exception as e:
            print(f"Error generating PDF report: {e}")
            raise

    def generate_summary_pdf_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate summary PDF report (compact version)

        :param analysis_result: Analysis result data
        :return: Path to generated PDF file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            period_str = f"{analysis_result.start_date.strftime('%B_%Y')}"
            filename = f"Laporan_Ringkasan_{period_str}_{timestamp}.pdf"
            filepath = os.path.join(self.output_directory, filename)

            # Generate summary PDF report
            self.pdf_generator.create_summary_report(
                analysis_result=analysis_result,
                output_path=filepath
            )

            return filepath

        except Exception as e:
            print(f"Error generating summary PDF report: {e}")
            raise

    def generate_excel_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate Excel report with detailed data

        :param analysis_result: Analysis result data
        :return: Path to generated Excel file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            period_str = f"{analysis_result.start_date.strftime('%B_%Y')}"
            filename = f"Laporan_Detail_{period_str}_{timestamp}.xlsx"
            filepath = os.path.join(self.output_directory, filename)

            # Generate Excel report
            self.excel_exporter.create_detailed_report(
                analysis_result=analysis_result,
                output_path=filepath
            )

            return filepath

        except Exception as e:
            print(f"Error generating Excel report: {e}")
            raise

    def generate_employee_performance_report(self, analysis_result: AnalysisResult,
                                            employee_ids: Optional[List[str]] = None) -> str:
        """
        Generate employee performance focused report

        :param analysis_result: Analysis result data
        :param employee_ids: Optional list of specific employee IDs to focus on
        :return: Path to generated PDF file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            period_str = f"{analysis_result.start_date.strftime('%B_%Y')}"
            filename = f"Laporan_Kinerja_Karyawan_{period_str}_{timestamp}.pdf"
            filepath = os.path.join(self.output_directory, filename)

            # Filter employees if specified
            filtered_result = analysis_result
            if employee_ids:
                filtered_result = self._filter_analysis_by_employees(analysis_result, employee_ids)

            # Generate employee performance report
            self.pdf_generator.create_employee_performance_report(
                analysis_result=filtered_result,
                output_path=filepath
            )

            return filepath

        except Exception as e:
            print(f"Error generating employee performance report: {e}")
            raise

    def generate_quality_assurance_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate quality assurance focused report

        :param analysis_result: Analysis result data
        :return: Path to generated PDF file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            period_str = f"{analysis_result.start_date.strftime('%B_%Y')}"
            filename = f"Laporan_Quality_Assurance_{period_str}_{timestamp}.pdf"
            filepath = os.path.join(self.output_directory, filename)

            # Generate quality assurance report
            self.pdf_generator.create_quality_assurance_report(
                analysis_result=analysis_result,
                output_path=filepath
            )

            return filepath

        except Exception as e:
            print(f"Error generating quality assurance report: {e}")
            raise

    def generate_template_compatible_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate template-compatible PDF report matching exact format specification

        :param analysis_result: Analysis result data
        :return: Path to generated PDF file
        """
        try:
            # Use same filename format as original system
            month_name = analysis_result.start_date.strftime("%B")
            year = analysis_result.start_date.strftime("%Y")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Laporan_Kinerja_Kerani_Mandor_Asisten_{month_name}_{year}_{timestamp}.pdf"
            filepath = os.path.join(self.output_directory, filename)

            # Generate template-compatible PDF report
            self.template_generator.create_template_compatible_report(
                analysis_result=analysis_result,
                output_path=filepath
            )

            return filepath

        except Exception as e:
            print(f"Error generating template-compatible report: {e}")
            raise

    def generate_multi_format_reports(self, analysis_result: AnalysisResult) -> Dict[str, str]:
        """
        Generate reports in multiple formats

        :param analysis_result: Analysis result data
        :return: Dictionary with format -> file path mapping
        """
        generated_files = {}

        try:
            # Generate template-compatible report (primary format matching original)
            generated_files['template_compatible'] = self.generate_template_compatible_report(analysis_result)

            # Generate comprehensive PDF
            generated_files['comprehensive_pdf'] = self.generate_comprehensive_pdf_report(analysis_result)

            # Generate summary PDF
            generated_files['summary_pdf'] = self.generate_summary_pdf_report(analysis_result)

            # Generate Excel report
            generated_files['excel'] = self.generate_excel_report(analysis_result)

            # Generate specialized reports
            generated_files['employee_performance'] = self.generate_employee_performance_report(analysis_result)

            # Generate quality assurance report if there are differences
            if analysis_result.grand_differences > 0:
                generated_files['quality_assurance'] = self.generate_quality_assurance_report(analysis_result)

        except Exception as e:
            print(f"Error generating multi-format reports: {e}")
            raise

        return generated_files

    def _filter_analysis_by_employees(self, analysis_result: AnalysisResult,
                                      employee_ids: List[str]) -> AnalysisResult:
        """
        Filter analysis result to include only specified employees

        :param analysis_result: Original analysis result
        :param employee_ids: List of employee IDs to include
        :return: Filtered analysis result
        """
        # Create new analysis result with same metadata
        filtered_result = AnalysisResult.create_empty(
            analysis_result.start_date,
            analysis_result.end_date,
            analysis_result.analyzed_estates
        )

        # Copy metadata
        filtered_result.analysis_duration_seconds = analysis_result.analysis_duration_seconds
        filtered_result.use_status_704_filter = analysis_result.use_status_704_filter
        filtered_result.analysis_version = analysis_result.analysis_version

        # Filter division summaries
        employee_id_set = set(employee_ids)
        for division_summary in analysis_result.get_division_summaries():
            # Filter employees in division
            filtered_employees = {}
            for emp_id, employee_metrics in division_summary.employee_details.items():
                if emp_id in employee_id_set:
                    filtered_employees[emp_id] = employee_metrics

            if filtered_employees:
                # Create filtered division summary
                filtered_summary = DivisionSummary(
                    estate_name=division_summary.estate_name,
                    division_id=division_summary.division_id,
                    division_name=division_summary.division_name,
                    kerani_total=sum(emp.kerani_transactions for emp in filtered_employees.values()),
                    mandor_total=sum(emp.mandor_transactions for emp in filtered_employees.values()),
                    asisten_total=sum(emp.asisten_transactions for emp in filtered_employees.values()),
                    verification_total=sum(emp.kerani_verified for emp in filtered_employees.values()),
                    difference_count=sum(emp.kerani_differences for emp in filtered_employees.values()),
                    employee_count=len(filtered_employees),
                    employee_details=filtered_employees
                )

                # Calculate rates
                filtered_summary.verification_rate = filtered_summary.get_verification_rate()
                filtered_summary.difference_rate = filtered_summary.get_difference_rate()

                filtered_result.add_division_summary(filtered_summary)

        return filtered_result

    def get_report_statistics(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Get statistics about reports that will be generated

        :param analysis_result: Analysis result data
        :return: Report statistics
        """
        stats = {
            'analysis_summary': analysis_result.get_analysis_summary(),
            'report_options': {
                'comprehensive_pdf': True,
                'summary_pdf': True,
                'excel_report': True,
                'employee_performance': True,
                'quality_assurance': analysis_result.grand_differences > 0
            },
            'data_size': {
                'total_divisions': analysis_result.total_divisions,
                'total_employees': len(analysis_result.get_all_employee_metrics()),
                'top_performers': len(analysis_result.get_top_performers()),
                'problematic_employees': len(analysis_result.get_problematic_employees())
            },
            'estimated_generation_time': {
                'pdf_comprehensive': 30,  # seconds
                'pdf_summary': 10,
                'excel': 20,
                'employee_performance': 15,
                'quality_assurance': 25 if analysis_result.grand_differences > 0 else 0
            }
        }

        # Calculate total estimated time
        total_time = sum(stats['estimated_generation_time'].values())
        stats['estimated_generation_time']['total'] = total_time

        return stats

    def validate_output_directory(self) -> Dict[str, Any]:
        """
        Validate output directory

        :return: Validation result
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Check if directory exists
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
                result['warnings'].append(f"Created output directory: {self.output_directory}")
            except Exception as e:
                result['is_valid'] = False
                result['errors'].append(f"Cannot create output directory: {e}")
                return result

        # Check if directory is writable
        if not os.access(self.output_directory, os.W_OK):
            result['is_valid'] = False
            result['errors'].append(f"Output directory is not writable: {self.output_directory}")

        # Check available disk space
        try:
            stat = os.statvfs(self.output_directory)
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_space_gb < 0.5:  # Less than 500MB
                result['warnings'].append(f"Low disk space: {free_space_gb:.2f}GB available")
        except:
            pass

        return result

    def cleanup_old_reports(self, days_to_keep: int = 30) -> int:
        """
        Clean up old report files

        :param days_to_keep: Number of days to keep files
        :return: Number of files deleted
        """
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)

        try:
            for filename in os.listdir(self.output_directory):
                filepath = os.path.join(self.output_directory, filename)
                if os.path.isfile(filepath):
                    file_mtime = os.path.getmtime(filepath)
                    if file_mtime < cutoff_time:
                        try:
                            os.remove(filepath)
                            deleted_count += 1
                        except Exception as e:
                            print(f"Error deleting old report {filename}: {e}")
        except Exception as e:
            print(f"Error cleaning up old reports: {e}")

        return deleted_count

    def get_report_file_list(self) -> List[Dict[str, Any]]:
        """
        Get list of existing report files

        :return: List of file information
        """
        files = []

        try:
            for filename in os.listdir(self.output_directory):
                filepath = os.path.join(self.output_directory, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'type': os.path.splitext(filename)[1].lower()
                    })
        except Exception as e:
            print(f"Error listing report files: {e}")

        # Sort by modification date (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files