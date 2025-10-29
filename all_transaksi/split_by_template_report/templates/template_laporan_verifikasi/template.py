"""
Template Laporan Verifikasi FFB Implementation

This module implements the complete template for FFB verification reports,
including GUI components, business logic, and report generation.

Author: Generated for Modular FFB Analysis System
Date: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
import threading

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Import base template classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.template_base import (
    BaseTemplate,
    TemplateConfigInterface,
    TemplateGUIInterface,
    TemplateBusinessLogicInterface,
    TemplateReportInterface
)


class VerifikasiConfigHandler(TemplateConfigInterface):
    """Configuration handler for Verifikasi template"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load template configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return self.config
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        required_keys = [
            "name", "version", "template_class",
            "gui_config", "business_logic_config", 
            "report_config", "sql_queries"
        ]
        
        for key in required_keys:
            if key not in self.config:
                return False
        return True


class VerifikasiGUIHandler(TemplateGUIInterface):
    """GUI handler for Verifikasi template"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_frame = None
        self.widgets = {}
        
    def create_template_frame(self, parent) -> tk.Frame:
        """Create template-specific GUI frame"""
        self.template_frame = ttk.LabelFrame(parent, text="Pengaturan Laporan Verifikasi", padding="10")
        
        # Date range selection
        date_frame = ttk.Frame(self.template_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="Periode Analisis:").pack(side="left")
        
        # Start date
        ttk.Label(date_frame, text="Dari:").pack(side="left", padx=(20, 5))
        self.widgets['start_date'] = tk.StringVar()
        start_date_entry = ttk.Entry(date_frame, textvariable=self.widgets['start_date'], width=12)
        start_date_entry.pack(side="left", padx=(0, 10))
        
        # End date
        ttk.Label(date_frame, text="Sampai:").pack(side="left", padx=(10, 5))
        self.widgets['end_date'] = tk.StringVar()
        end_date_entry = ttk.Entry(date_frame, textvariable=self.widgets['end_date'], width=12)
        end_date_entry.pack(side="left")
        
        # Set default dates
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=self.config.get('gui_config', {}).get('default_date_range_days', 30))
        self.widgets['start_date'].set(start_date.strftime('%Y-%m-%d'))
        self.widgets['end_date'].set(end_date.strftime('%Y-%m-%d'))
        
        # Division selection
        div_frame = ttk.LabelFrame(self.template_frame, text="Pilih Divisi", padding="5")
        div_frame.pack(fill="both", expand=True, pady=10)
        
        # Division tree
        tree_frame = ttk.Frame(div_frame)
        tree_frame.pack(fill="both", expand=True)
        
        self.widgets['division_tree'] = ttk.Treeview(tree_frame, height=6, selectmode="extended")
        self.widgets['division_tree'].heading("#0", text="Divisi", anchor="w")
        
        # Scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.widgets['division_tree'].yview)
        self.widgets['division_tree'].configure(yscrollcommand=tree_scrollbar.set)
        
        self.widgets['division_tree'].pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Division control buttons
        div_control_frame = ttk.Frame(div_frame)
        div_control_frame.pack(fill="x", pady=5)
        
        ttk.Button(div_control_frame, text="Pilih Semua", 
                  command=self._select_all_divisions).pack(side="left", padx=(0, 5))
        ttk.Button(div_control_frame, text="Hapus Pilihan", 
                  command=self._clear_division_selection).pack(side="left")
        
        # Additional filters
        if self.config.get('gui_config', {}).get('additional_filters', {}).get('show_transno_filter', False):
            filter_frame = ttk.LabelFrame(self.template_frame, text="Filter Tambahan", padding="5")
            filter_frame.pack(fill="x", pady=5)
            
            ttk.Label(filter_frame, text="Filter TransNo:").pack(side="left")
            self.widgets['transno_filter'] = tk.StringVar()
            ttk.Entry(filter_frame, textvariable=self.widgets['transno_filter'], width=20).pack(side="left", padx=(5, 0))
        
        return self.template_frame
    
    def _select_all_divisions(self):
        """Select all divisions in the tree"""
        for item in self.widgets['division_tree'].get_children():
            self.widgets['division_tree'].selection_add(item)
    
    def _clear_division_selection(self):
        """Clear all division selections"""
        self.widgets['division_tree'].selection_remove(self.widgets['division_tree'].selection())
    
    def populate_divisions(self, divisions: List[str]):
        """Populate division tree with available divisions"""
        # Clear existing items
        for item in self.widgets['division_tree'].get_children():
            self.widgets['division_tree'].delete(item)
        
        # Add divisions
        for division in divisions:
            self.widgets['division_tree'].insert("", "end", text=division, values=[division])
        
        # Select all by default if configured
        if self.config.get('gui_config', {}).get('division_selection', {}).get('default_all_selected', True):
            self._select_all_divisions()
    
    def get_template_inputs(self) -> Dict[str, Any]:
        """Get user inputs from template GUI"""
        selected_divisions = []
        for item in self.widgets['division_tree'].selection():
            division = self.widgets['division_tree'].item(item, "text")
            selected_divisions.append(division)
        
        inputs = {
            'start_date': self.widgets['start_date'].get(),
            'end_date': self.widgets['end_date'].get(),
            'selected_divisions': selected_divisions
        }
        
        # Add additional filters if available
        if 'transno_filter' in self.widgets:
            inputs['transno_filter'] = self.widgets['transno_filter'].get()
        
        return inputs
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate user inputs"""
        try:
            # Validate dates
            start_date_str = self.widgets['start_date'].get()
            end_date_str = self.widgets['end_date'].get()
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                return False, "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
            
            # Validate division selection
            selected_divisions = []
            for item in self.widgets['division_tree'].selection():
                selected_divisions.append(self.widgets['division_tree'].item(item, "text"))
            
            if not selected_divisions:
                return False, "Pilih minimal satu divisi untuk dianalisis"
            
            return True, "Validasi berhasil"
            
        except ValueError as e:
            return False, f"Format tanggal tidak valid. Gunakan format YYYY-MM-DD"
        except Exception as e:
            return False, f"Error validasi: {str(e)}"
    
    def reset_inputs(self) -> None:
        """Reset all input fields to default values"""
        # Reset dates to default range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=self.config.get('gui_config', {}).get('default_date_range_days', 30))
        self.widgets['start_date'].set(start_date.strftime('%Y-%m-%d'))
        self.widgets['end_date'].set(end_date.strftime('%Y-%m-%d'))
        
        # Clear division selection
        self._clear_division_selection()
        
        # Reset additional filters
        if 'transno_filter' in self.widgets:
            self.widgets['transno_filter'].set("")


class VerifikasiBusinessLogic(TemplateBusinessLogicInterface):
    """Business logic handler for Verifikasi template"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def process_data(self, raw_data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Process raw data according to template logic"""
        try:
            processed_data = raw_data.copy()
            
            # Add verification status if not present
            if 'STATUS_VERIFIKASI' not in processed_data.columns:
                processed_data['STATUS_VERIFIKASI'] = 'PENDING'
            
            # Convert date column to datetime
            if 'TANGGAL' in processed_data.columns:
                processed_data['TANGGAL'] = pd.to_datetime(processed_data['TANGGAL'])
            
            # Add calculated fields
            processed_data['BERAT_NETTO_CALC'] = processed_data.get('BERAT_BRUTO', 0) - processed_data.get('BERAT_TARA', 0)
            
            # Check for data consistency
            if config.get('business_logic_config', {}).get('verification_rules', {}).get('check_data_consistency', True):
                processed_data['KONSISTENSI_BERAT'] = abs(
                    processed_data.get('BERAT_NETTO', 0) - processed_data['BERAT_NETTO_CALC']
                ) < 0.01
            
            # Identify duplicates
            if config.get('business_logic_config', {}).get('verification_rules', {}).get('check_duplicate_transno', True):
                processed_data['IS_DUPLICATE'] = processed_data.duplicated(subset=['TRANSNO'], keep=False)
            
            # Sort by division and date
            if config.get('business_logic_config', {}).get('analysis_options', {}).get('group_by_division', True):
                processed_data = processed_data.sort_values(['DIVISI', 'TANGGAL', 'TRANSNO'])
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            return raw_data
    
    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate processed data"""
        try:
            # Check required columns
            required_columns = self.config.get('validation_rules', {}).get('required_columns', [])
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Check data types
            data_types = self.config.get('validation_rules', {}).get('data_types', {})
            for column, expected_type in data_types.items():
                if column in data.columns:
                    if expected_type == 'numeric' and not pd.api.types.is_numeric_dtype(data[column]):
                        return False, f"Column {column} should be numeric"
                    elif expected_type == 'datetime' and not pd.api.types.is_datetime64_any_dtype(data[column]):
                        return False, f"Column {column} should be datetime"
            
            # Check business rules
            business_rules = self.config.get('validation_rules', {}).get('business_rules', {})
            if 'min_weight' in business_rules and 'BERAT_NETTO' in data.columns:
                min_weight = business_rules['min_weight']
                invalid_weights = data[data['BERAT_NETTO'] < min_weight]
                if not invalid_weights.empty:
                    return False, f"Found {len(invalid_weights)} records with weight below minimum ({min_weight})"
            
            if 'max_weight' in business_rules and 'BERAT_NETTO' in data.columns:
                max_weight = business_rules['max_weight']
                invalid_weights = data[data['BERAT_NETTO'] > max_weight]
                if not invalid_weights.empty:
                    return False, f"Found {len(invalid_weights)} records with weight above maximum ({max_weight})"
            
            return True, "Data validation successful"
            
        except Exception as e:
            return False, f"Data validation error: {str(e)}"
    
    def generate_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics from processed data"""
        try:
            summary = {
                'total_records': len(data),
                'total_divisions': data['DIVISI'].nunique() if 'DIVISI' in data.columns else 0,
                'date_range': {
                    'start': data['TANGGAL'].min().strftime('%Y-%m-%d') if 'TANGGAL' in data.columns else '',
                    'end': data['TANGGAL'].max().strftime('%Y-%m-%d') if 'TANGGAL' in data.columns else ''
                }
            }
            
            # Weight statistics
            if 'BERAT_NETTO' in data.columns:
                summary['weight_stats'] = {
                    'total_weight': data['BERAT_NETTO'].sum(),
                    'average_weight': data['BERAT_NETTO'].mean(),
                    'min_weight': data['BERAT_NETTO'].min(),
                    'max_weight': data['BERAT_NETTO'].max()
                }
            
            # Division summary
            if 'DIVISI' in data.columns:
                division_summary = data.groupby('DIVISI').agg({
                    'TRANSNO': 'count',
                    'BERAT_NETTO': ['sum', 'mean'] if 'BERAT_NETTO' in data.columns else 'count'
                }).round(2)
                summary['division_summary'] = division_summary.to_dict()
            
            # Verification issues
            if 'IS_DUPLICATE' in data.columns:
                summary['duplicate_count'] = data['IS_DUPLICATE'].sum()
            
            if 'KONSISTENSI_BERAT' in data.columns:
                summary['inconsistent_weight_count'] = (~data['KONSISTENSI_BERAT']).sum()
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {'error': str(e)}


class VerifikasiReportGenerator(TemplateReportInterface):
    """Report generator for Verifikasi template"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def generate_excel_report(self, data: pd.DataFrame, output_path: str, config: Dict[str, Any]) -> bool:
        """Generate Excel report"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main data sheet
                data.to_excel(writer, sheet_name='Data Verifikasi', index=False)
                
                # Summary sheet if configured
                if config.get('report_config', {}).get('excel_format', {}).get('include_summary_sheet', True):
                    business_logic = VerifikasiBusinessLogic(config)
                    summary = business_logic.generate_summary(data)
                    
                    # Create summary DataFrame
                    summary_data = []
                    for key, value in summary.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                summary_data.append({'Metric': f"{key}_{sub_key}", 'Value': sub_value})
                        else:
                            summary_data.append({'Metric': key, 'Value': value})
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Ringkasan', index=False)
                
                # Division analysis sheet
                if 'DIVISI' in data.columns:
                    division_analysis = data.groupby('DIVISI').agg({
                        'TRANSNO': 'count',
                        'BERAT_NETTO': ['sum', 'mean', 'min', 'max'] if 'BERAT_NETTO' in data.columns else 'count'
                    }).round(2)
                    division_analysis.to_excel(writer, sheet_name='Analisis per Divisi')
            
            return True
            
        except Exception as e:
            print(f"Error generating Excel report: {str(e)}")
            return False
    
    def generate_pdf_report(self, data: pd.DataFrame, output_path: str, config: Dict[str, Any]) -> bool:
        """Generate PDF report"""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=landscape(A4) if config.get('report_config', {}).get('pdf_format', {}).get('page_orientation') == 'landscape' else A4,
                leftMargin=30,
                rightMargin=30,
                topMargin=40,
                bottomMargin=40
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            if config.get('report_config', {}).get('pdf_format', {}).get('include_header', True):
                header_style = ParagraphStyle(
                    'CompanyHeader',
                    parent=styles['Normal'],
                    fontSize=12,
                    textColor=colors.HexColor('#2E4057'),
                    alignment=1,
                    spaceAfter=5,
                    fontName='Helvetica-Bold'
                )
                
                company_header = Paragraph(
                    "<b>PT. REBINMAS JAYA</b><br/>LAPORAN VERIFIKASI FFB SCANNER", 
                    header_style
                )
                story.append(company_header)
                story.append(Spacer(1, 20))
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1A365D'),
                spaceAfter=10,
                alignment=1
            )
            
            title = Paragraph("LAPORAN VERIFIKASI DATA FFB", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Summary section
            business_logic = VerifikasiBusinessLogic(config)
            summary = business_logic.generate_summary(data)
            
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=5
            )
            
            story.append(Paragraph("<b>RINGKASAN LAPORAN</b>", summary_style))
            story.append(Paragraph(f"Total Transaksi: {summary.get('total_records', 0)}", summary_style))
            story.append(Paragraph(f"Total Divisi: {summary.get('total_divisions', 0)}", summary_style))
            
            if 'date_range' in summary:
                story.append(Paragraph(f"Periode: {summary['date_range'].get('start', '')} s/d {summary['date_range'].get('end', '')}", summary_style))
            
            if 'weight_stats' in summary:
                weight_stats = summary['weight_stats']
                story.append(Paragraph(f"Total Berat: {weight_stats.get('total_weight', 0):,.2f} kg", summary_style))
                story.append(Paragraph(f"Rata-rata Berat: {weight_stats.get('average_weight', 0):,.2f} kg", summary_style))
            
            story.append(Spacer(1, 20))
            
            # Data table (first 50 rows for PDF)
            if not data.empty:
                story.append(Paragraph("<b>DATA VERIFIKASI (50 Baris Pertama)</b>", summary_style))
                story.append(Spacer(1, 10))
                
                # Select columns for PDF table
                display_columns = ['TRANSNO', 'DIVISI', 'TANGGAL', 'BERAT_NETTO']
                display_columns = [col for col in display_columns if col in data.columns]
                
                if display_columns:
                    table_data = [display_columns]  # Header
                    
                    # Add data rows (limit to 50)
                    for _, row in data[display_columns].head(50).iterrows():
                        table_row = []
                        for col in display_columns:
                            value = row[col]
                            if pd.isna(value):
                                table_row.append('')
                            elif col == 'TANGGAL' and hasattr(value, 'strftime'):
                                table_row.append(value.strftime('%Y-%m-%d'))
                            elif isinstance(value, (int, float)):
                                table_row.append(f"{value:,.2f}" if isinstance(value, float) else str(value))
                            else:
                                table_row.append(str(value))
                        table_data.append(table_row)
                    
                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(table)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            return False
    
    def get_report_filename(self, config: Dict[str, Any]) -> str:
        """Generate appropriate filename for reports"""
        try:
            filename_format = config.get('report_config', {}).get('filename_format', 
                                                                 'Laporan_Verifikasi_FFB_{timestamp}')
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = filename_format.format(
                timestamp=timestamp,
                date=datetime.now().strftime('%Y%m%d')
            )
            
            return filename
            
        except Exception as e:
            print(f"Error generating filename: {str(e)}")
            return f"Laporan_Verifikasi_FFB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


class TemplateVerifikasiFFB(BaseTemplate):
    """
    Main template class for FFB Verification reports
    """
    
    def __init__(self, template_name: str, template_path: str):
        super().__init__(template_name, template_path)
        
        # Initialize handlers
        self._config_handler = None
        self._gui_handler = None
        self._business_logic = None
        self._report_generator = None
    
    def initialize_template(self) -> bool:
        """Initialize template components and configuration"""
        try:
            # Load base configuration
            if not self.load_base_config():
                return False
            
            # Initialize handlers
            self._config_handler = VerifikasiConfigHandler(self.config_path)
            self._config_handler.load_config(self.config_path)
            
            if not self._config_handler.validate_config():
                print("Configuration validation failed")
                return False
            
            self._gui_handler = VerifikasiGUIHandler(self.config)
            self._business_logic = VerifikasiBusinessLogic(self.config)
            self._report_generator = VerifikasiReportGenerator(self.config)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Template initialization failed: {str(e)}")
            return False
    
    def get_config_handler(self) -> TemplateConfigInterface:
        """Get template configuration handler"""
        return self._config_handler
    
    def get_gui_handler(self) -> TemplateGUIInterface:
        """Get template GUI handler"""
        return self._gui_handler
    
    def get_business_logic(self) -> TemplateBusinessLogicInterface:
        """Get template business logic handler"""
        return self._business_logic
    
    def get_report_generator(self) -> TemplateReportInterface:
        """Get template report generator"""
        return self._report_generator
    
    def _execute_database_query(self, database_connector, template_inputs: Dict[str, Any], analysis_params: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Execute database query specific to this template"""
        try:
            # Get query from config
            main_query = self.config.get('sql_queries', {}).get('main_query', '')
            
            if not main_query:
                print("Main query not found in configuration")
                return None
            
            # Build division filter
            selected_divisions = template_inputs.get('selected_divisions', [])
            if selected_divisions:
                division_placeholders = ', '.join(['?' for _ in selected_divisions])
                division_filter = f"AND DIVISI IN ({division_placeholders})"
            else:
                division_filter = ""
            
            # Replace placeholder in query
            query = main_query.replace('{division_filter}', division_filter)
            
            # Prepare parameters
            params = [template_inputs['start_date'], template_inputs['end_date']]
            if selected_divisions:
                params.extend(selected_divisions)
            
            # Execute query
            result = database_connector.execute_query(query, params)
            
            if result and 'data' in result:
                return result['data']
            else:
                print("No data returned from query")
                return None
                
        except Exception as e:
            print(f"Database query execution failed: {str(e)}")
            return None
    
    def load_divisions(self, database_connector) -> List[str]:
        """Load available divisions from database"""
        try:
            division_query = self.config.get('sql_queries', {}).get('division_query', 
                                                                   'SELECT DISTINCT DIVISI FROM TRANSAKSI_FFB ORDER BY DIVISI')
            
            result = database_connector.execute_query(division_query)
            
            if result and 'data' in result:
                divisions = result['data']['DIVISI'].tolist()
                return divisions
            else:
                return []
                
        except Exception as e:
            print(f"Error loading divisions: {str(e)}")
            return []