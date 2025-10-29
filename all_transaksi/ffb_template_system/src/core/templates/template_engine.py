"""
FFB Template Engine - Core Template Processing System
Template-based report generation engine for FFB Analysis
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re
import pandas as pd
from jinja2 import Template, Environment, BaseLoader

from ..database.connection import FirebirdConnectionManager
from ..reports.jasper_service import JasperReportService

logger = logging.getLogger(__name__)


class FFRTemplateEngine:
    """
    Template Engine untuk FFB Analysis System
    Menangani template processing, parameter substitution, dan report generation
    """

    def __init__(self, connection_manager: FirebirdConnectionManager):
        self.connection_manager = connection_manager
        self.jasper_service = JasperReportService(connection_manager)
        self.template_dir = Path("templates")
        self.sql_dir = self.template_dir / "sql"
        self.jasper_dir = self.template_dir / "jasper"
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)

        # Template categories
        self.template_categories = {
            "KINERJA_KARYAWAN": "Laporan Kinerja Karyawan",
            "FFB_ANALYSIS": "FFB Transaction Analysis",
            "DATA_QUALITY": "Data Quality Report",
            "SUMMARY": "Executive Summary"
        }

    def load_template(self, template_file: str) -> Dict[str, Any]:
        """Load template definition dari JSON file"""
        try:
            template_path = self.template_dir / template_file
            if not template_path.exists():
                raise FileNotFoundError(f"Template file not found: {template_path}")

            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            logger.info(f"Loaded template: {template_data.get('name', template_file)}")
            return template_data

        except Exception as e:
            logger.error(f"Error loading template {template_file}: {e}")
            raise

    def load_sql_template(self, sql_file: str) -> str:
        """Load SQL template dari file"""
        try:
            sql_path = self.sql_dir / sql_file
            if not sql_path.exists():
                raise FileNotFoundError(f"SQL template file not found: {sql_path}")

            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            logger.info(f"Loaded SQL template: {sql_file}")
            return sql_content

        except Exception as e:
            logger.error(f"Error loading SQL template {sql_file}: {e}")
            raise

    def validate_parameters(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate required parameters against template definition"""
        errors = []

        if 'parameters' not in template:
            return True, []

        for param_def in template['parameters']:
            param_name = param_def['name']
            param_required = param_def.get('required', False)

            if param_required and param_name not in parameters:
                errors.append(f"Required parameter '{param_name}' is missing")

            if param_name in parameters:
                # Type validation
                param_type = param_def.get('type', 'STRING')
                param_value = parameters[param_name]

                if param_type == 'DATE' and param_value:
                    try:
                        if isinstance(param_value, str):
                            datetime.strptime(param_value, '%Y-%m-%d')
                        elif isinstance(param_value, (date, datetime)):
                            pass  # Valid date object
                        else:
                            errors.append(f"Parameter '{param_name}' must be a valid date")
                    except ValueError:
                        errors.append(f"Parameter '{param_name}' must be in YYYY-MM-DD format")

                elif param_type == 'MULTI_SELECT' and param_value:
                    if not isinstance(param_value, (list, tuple)):
                        errors.append(f"Parameter '{param_name}' must be a list")

        return len(errors) == 0, errors

    def substitute_parameters(self, sql_template: str, parameters: Dict[str, Any],
                            template: Dict[str, Any]) -> str:
        """Substitute parameters into SQL template"""
        try:
            # Create Jinja2 environment for parameter substitution
            env = Environment(loader=BaseLoader())
            jinja_template = env.from_string(sql_template)

            # Prepare template variables
            template_vars = {}

            # Add direct parameters
            for key, value in parameters.items():
                template_vars[key] = value

            # Add derived parameters
            if 'START_DATE' in parameters and 'END_DATE' in parameters:
                start_date = parameters['START_DATE']
                end_date = parameters['END_DATE']

                # Generate month tables
                month_tables = self._generate_month_tables(start_date, end_date)
                template_vars['MONTH_TABLES'] = ', '.join(month_tables)
                template_vars['MONTH_TABLE'] = month_tables[0] if month_tables else 'FFBSCANNERDATA01'

                # Generate estate list string
                if 'ESTATES' in parameters:
                    estates = parameters['ESTATES']
                    if isinstance(estates, list):
                        template_vars['ESTATE_NAMES'] = ', '.join(estates)
                    else:
                        template_vars['ESTATE_NAMES'] = str(estates)

                # Generate status filter
                use_status_filter = parameters.get('USE_STATUS_704_FILTER', False)
                if use_status_filter:
                    template_vars['STATUS_FILTER'] = "AND (e.TRANSSTATUS = '704' OR e.RECORDTAG = 'PM')"
                    template_vars['STATUS_704_FILTER'] = "AND t2.TRANSSTATUS = '704'"
                else:
                    template_vars['STATUS_FILTER'] = ""
                    template_vars['STATUS_704_FILTER'] = ""

                # Include zero data flag
                template_vars['INCLUDE_ZERO_DATA'] = str(parameters.get('INCLUDE_ZERO_DATA', False)).lower()

            # Render SQL with parameters
            rendered_sql = jinja_template.render(**template_vars)

            logger.info(f"SQL parameter substitution completed")
            return rendered_sql

        except Exception as e:
            logger.error(f"Error in parameter substitution: {e}")
            raise

    def _generate_month_tables(self, start_date: str, end_date: str) -> List[str]:
        """Generate list of month tables for date range"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            month_tables = []
            current = start

            while current <= end:
                month_table = f"FFBSCANNERDATA{current.month:02d}"
                if month_table not in month_tables:
                    month_tables.append(month_table)

                # Move to next month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    current = current.replace(month=current.month + 1, day=1)

            return month_tables

        except Exception as e:
            logger.error(f"Error generating month tables: {e}")
            return ["FFBSCANNERDATA01"]  # Default fallback

    def execute_template(self, template_file: str, parameters: Dict[str, Any],
                        estates: List[str] = None) -> Dict[str, Any]:
        """
        Execute template dengan multi-estate support

        Args:
            template_file: Template definition file (JSON)
            parameters: Template parameters
            estates: List of estates to process (if None, use from parameters)

        Returns:
            Dictionary dengan execution results
        """
        try:
            # Load template definition
            template = self.load_template(template_file)

            # Validate parameters
            is_valid, errors = self.validate_parameters(template, parameters)
            if not is_valid:
                return {
                    'success': False,
                    'errors': errors,
                    'message': 'Parameter validation failed'
                }

            # Get estates to process
            if estates is None:
                estates = parameters.get('ESTATES', [])
                if isinstance(estates, str):
                    estates = [estates]

            if not estates:
                return {
                    'success': False,
                    'errors': ['No estates specified'],
                    'message': 'No estates to process'
                }

            # Load SQL template
            sql_template_file = template.get('sql_template', 'laporan_kinerja_karyawan.sql')
            sql_template = self.load_sql_template(sql_template_file)

            # Execute for each estate
            all_results = []
            execution_errors = []

            for estate_name in estates:
                try:
                    # Get estate database connection
                    estate_db_path = self.connection_manager.get_estate_db_path(estate_name)
                    if not estate_db_path:
                        execution_errors.append(f"Estate {estate_name}: Database path not found")
                        continue

                    # Execute query for this estate
                    estate_result = self._execute_estate_query(
                        estate_name, estate_db_path, sql_template,
                        parameters, template
                    )

                    if estate_result['success']:
                        all_results.extend(estate_result['data'])
                        logger.info(f"Estate {estate_name}: {len(estate_result['data'])} records processed")
                    else:
                        execution_errors.append(f"Estate {estate_name}: {estate_result['error']}")

                except Exception as e:
                    error_msg = f"Estate {estate_name}: {str(e)}"
                    execution_errors.append(error_msg)
                    logger.error(error_msg)

            # Generate report if we have data
            report_files = []
            if all_results:
                try:
                    report_files = self._generate_reports(template, all_results, parameters)
                except Exception as e:
                    execution_errors.append(f"Report generation failed: {str(e)}")
                    logger.error(f"Report generation failed: {e}")

            return {
                'success': len(all_results) > 0,
                'template_name': template.get('name'),
                'total_records': len(all_results),
                'estates_processed': len([r for r in all_results if r.get('ESTATE_NAME')]),
                'data': all_results,
                'report_files': report_files,
                'errors': execution_errors,
                'execution_time': datetime.now().isoformat(),
                'message': f"Processed {len(all_results)} records from {len(estates)} estates"
            }

        except Exception as e:
            logger.error(f"Template execution failed: {e}")
            return {
                'success': False,
                'errors': [str(e)],
                'message': 'Template execution failed'
            }

    def _execute_estate_query(self, estate_name: str, db_path: str, sql_template: str,
                            parameters: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query for specific estate"""
        try:
            # Create estate-specific connection
            connector = self.connection_manager.create_connection(db_path)
            if not connector.test_connection():
                return {
                    'success': False,
                    'error': f'Failed to connect to {estate_name} database'
                }

            # Prepare estate-specific parameters
            estate_params = parameters.copy()
            estate_params['ESTATE_NAME'] = estate_name

            # Substitute parameters in SQL
            rendered_sql = self.substitute_parameters(sql_template, estate_params, template)

            # Execute query
            result = connector.execute_query(rendered_sql)
            df = connector.to_pandas(result)

            # Add metadata
            df['ESTATE_NAME'] = estate_name
            df['REPORT_START_DATE'] = parameters.get('START_DATE')
            df['REPORT_END_DATE'] = parameters.get('END_DATE')
            df['GENERATED_AT'] = datetime.now()

            return {
                'success': True,
                'data': df.to_dict('records'),
                'query': rendered_sql,
                'record_count': len(df)
            }

        except Exception as e:
            logger.error(f"Error executing query for {estate_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_reports(self, template: Dict[str, Any], data: List[Dict],
                         parameters: Dict[str, Any]) -> List[str]:
        """Generate reports using Jasper service"""
        report_files = []

        try:
            # Convert data to DataFrame for Jasper
            df = pd.DataFrame(data)

            # Prepare Jasper parameters
            jasper_params = {
                'REPORT_START_DATE': parameters.get('START_DATE', ''),
                'REPORT_END_DATE': parameters.get('END_DATE', ''),
                'ESTATE_NAMES': ', '.join(parameters.get('ESTATES', [])),
                'GENERATED_BY': 'FFB Template System'
            }

            # Generate PDF report
            jasper_template = template.get('jasper_template', 'laporan_kinerja_karyawan.jrxml')
            jasper_path = self.jasper_dir / jasper_template

            if jasper_path.exists():
                output_filename = f"{template['template_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                output_path = self.output_dir / output_filename

                # Use Jasper service to generate report
                success, message, pdf_data = self.jasper_service.generate_report(
                    jasper_template, df, jasper_params, str(output_path)
                )

                if success and output_path.exists():
                    report_files.append(str(output_path))
                    logger.info(f"Generated report: {output_path}")
                else:
                    logger.warning(f"Jasper report generation failed: {message}")
            else:
                logger.warning(f"Jasper template not found: {jasper_path}")

            # Generate Excel report as fallback
            excel_filename = f"{template['template_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_path = self.output_dir / excel_filename

            df.to_excel(excel_path, index=False)
            report_files.append(str(excel_path))
            logger.info(f"Generated Excel report: {excel_path}")

        except Exception as e:
            logger.error(f"Error generating reports: {e}")

        return report_files

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        templates = []

        try:
            for template_file in self.template_dir.glob("*.json"):
                try:
                    template = self.load_template(template_file.name)
                    templates.append({
                        'file': template_file.name,
                        'name': template.get('name', template_file.stem),
                        'description': template.get('description', ''),
                        'category': template.get('category', ''),
                        'version': template.get('version', '1.0.0'),
                        'created_date': template.get('created_date', ''),
                        'parameters': len(template.get('parameters', []))
                    })
                except Exception as e:
                    logger.warning(f"Error loading template {template_file}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error listing templates: {e}")

        return sorted(templates, key=lambda x: x['name'])

    def get_template_info(self, template_file: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific template"""
        try:
            template = self.load_template(template_file)

            return {
                'template_id': template.get('template_id'),
                'name': template.get('name'),
                'description': template.get('description'),
                'category': template.get('category'),
                'version': template.get('version'),
                'created_by': template.get('created_by'),
                'created_date': template.get('created_date'),
                'parameters': template.get('parameters', []),
                'sql_queries': template.get('sql_queries', {}),
                'report_structure': template.get('report_structure', {}),
                'output_formats': template.get('output_formats', ['PDF'])
            }

        except Exception as e:
            logger.error(f"Error getting template info for {template_file}: {e}")
            return None