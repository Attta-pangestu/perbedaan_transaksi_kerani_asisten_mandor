"""
Validation Service
Service for validating user inputs and system configurations
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

from business.models.report_template import ReportTemplate
from business.models.report_request import ReportRequest
from infrastructure.exceptions.custom_exceptions import *


class ValidationService:
    """
    Service for validating inputs and configurations
    """
    
    def __init__(self):
        """Initialize validation service"""
        self.logger = logging.getLogger(__name__)
        
        # Validation rules
        self.month_pattern = re.compile(r'^\d{4}-\d{2}$')
        self.estate_name_pattern = re.compile(r'^[A-Za-z0-9_\-\s]+$')
        self.supported_formats = ['PDF', 'Excel', 'CSV', 'JSON']
        
        # Limits
        self.max_estates = 50
        self.max_filename_length = 200
        self.min_estate_name_length = 2
        self.max_estate_name_length = 50
    
    def validate_month_selection(self, month: str) -> Tuple[bool, List[str]]:
        """
        Validate month selection
        
        Args:
            month: Month string in YYYY-MM format
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not month:
            errors.append("Pemilihan bulan diperlukan")
            return False, errors
        
        if not self.month_pattern.match(month):
            errors.append("Format bulan tidak valid. Gunakan format YYYY-MM")
            return False, errors
        
        try:
            # Parse and validate date
            year, month_num = month.split('-')
            year = int(year)
            month_num = int(month_num)
            
            # Check year range
            current_year = datetime.now().year
            if year < 2020 or year > current_year + 1:
                errors.append(f"Tahun harus antara 2020 dan {current_year + 1}")
            
            # Check month range
            if month_num < 1 or month_num > 12:
                errors.append("Bulan harus antara 01 dan 12")
            
            # Check if future date (optional warning)
            selected_date = datetime(year, month_num, 1)
            if selected_date > datetime.now():
                # This is a warning, not an error
                self.logger.warning(f"Selected month {month} is in the future")
            
        except ValueError:
            errors.append("Format bulan tidak valid")
        
        return len(errors) == 0, errors
    
    def validate_estate_selection(self, estates: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate estate selection
        
        Args:
            estates: List of selected estate names
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not estates:
            errors.append("Minimal satu estate harus dipilih")
            return False, errors
        
        if len(estates) > self.max_estates:
            errors.append(f"Maksimal {self.max_estates} estate dapat dipilih")
        
        # Validate each estate name
        for estate in estates:
            if not estate or not estate.strip():
                errors.append("Nama estate tidak boleh kosong")
                continue
            
            estate = estate.strip()
            
            if len(estate) < self.min_estate_name_length:
                errors.append(f"Nama estate '{estate}' terlalu pendek (minimal {self.min_estate_name_length} karakter)")
            
            if len(estate) > self.max_estate_name_length:
                errors.append(f"Nama estate '{estate}' terlalu panjang (maksimal {self.max_estate_name_length} karakter)")
            
            if not self.estate_name_pattern.match(estate):
                errors.append(f"Nama estate '{estate}' mengandung karakter tidak valid")
        
        # Check for duplicates
        unique_estates = set(estate.strip().lower() for estate in estates)
        if len(unique_estates) != len(estates):
            errors.append("Terdapat estate yang duplikat dalam pilihan")
        
        return len(errors) == 0, errors
    
    def validate_template_selection(self, template: Optional[ReportTemplate]) -> Tuple[bool, List[str]]:
        """
        Validate template selection
        
        Args:
            template: Selected report template
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not template:
            errors.append("Template laporan harus dipilih")
            return False, errors
        
        # Validate template itself
        if not template.is_valid():
            template_errors = template.get_validation_errors()
            errors.extend([f"Template tidak valid: {error}" for error in template_errors])
        
        return len(errors) == 0, errors
    
    def validate_export_settings(self, export_settings: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate export settings
        
        Args:
            export_settings: Export configuration
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate formats
        formats = export_settings.get('formats', [])
        if not formats:
            errors.append("Minimal satu format export harus dipilih")
        else:
            for format_name in formats:
                if format_name not in self.supported_formats:
                    errors.append(f"Format '{format_name}' tidak didukung")
        
        # Validate output directory
        output_dir = export_settings.get('output_directory', '')
        if not output_dir:
            errors.append("Direktori output harus ditentukan")
        else:
            try:
                output_path = Path(output_dir)
                if not output_path.parent.exists():
                    errors.append(f"Direktori parent '{output_path.parent}' tidak ada")
            except Exception as e:
                errors.append(f"Path direktori output tidak valid: {str(e)}")
        
        # Validate filename prefix
        filename_prefix = export_settings.get('filename_prefix', '')
        if not filename_prefix:
            errors.append("Prefix nama file harus ditentukan")
        elif len(filename_prefix) > self.max_filename_length:
            errors.append(f"Prefix nama file terlalu panjang (maksimal {self.max_filename_length} karakter)")
        elif not re.match(r'^[A-Za-z0-9_\-\s]+$', filename_prefix):
            errors.append("Prefix nama file mengandung karakter tidak valid")
        
        return len(errors) == 0, errors
    
    def validate_report_request(self, request: ReportRequest) -> Tuple[bool, List[str]]:
        """
        Validate complete report request
        
        Args:
            request: Report generation request
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        all_errors = []
        
        # Validate month
        month_valid, month_errors = self.validate_month_selection(request.selected_month)
        all_errors.extend(month_errors)
        
        # Validate estates
        estates_valid, estate_errors = self.validate_estate_selection(request.selected_estates)
        all_errors.extend(estate_errors)
        
        # Validate template
        template_valid, template_errors = self.validate_template_selection(request.template)
        all_errors.extend(template_errors)
        
        # Validate export settings
        export_valid, export_errors = self.validate_export_settings(request.export_settings)
        all_errors.extend(export_errors)
        
        # Additional cross-validation
        if month_valid and template_valid and estates_valid:
            # Check template compatibility with estates
            if not request.template.supports_multi_estate() and len(request.selected_estates) > 1:
                all_errors.append("Template yang dipilih tidak mendukung multi-estate")
            
            # Check if template supports selected formats
            supported_formats = request.template.get_supported_formats()
            requested_formats = request.export_settings.get('formats', [])
            
            for format_name in requested_formats:
                if format_name not in supported_formats:
                    all_errors.append(f"Template tidak mendukung format '{format_name}'")
        
        return len(all_errors) == 0, all_errors
    
    def validate_system_configuration(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate system configuration
        
        Args:
            config: System configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate required configuration keys
        required_keys = ['estates', 'template_directory', 'default_output_directory']
        for key in required_keys:
            if key not in config:
                errors.append(f"Konfigurasi '{key}' diperlukan")
        
        # Validate estates configuration
        if 'estates' in config:
            estates_config = config['estates']
            if not isinstance(estates_config, list):
                errors.append("Konfigurasi estates harus berupa list")
            elif len(estates_config) == 0:
                errors.append("Minimal satu estate harus dikonfigurasi")
            else:
                for i, estate in enumerate(estates_config):
                    if not isinstance(estate, dict):
                        errors.append(f"Estate ke-{i+1} harus berupa dictionary")
                        continue
                    
                    if 'name' not in estate:
                        errors.append(f"Estate ke-{i+1} harus memiliki 'name'")
                    
                    if 'database_config' not in estate:
                        errors.append(f"Estate ke-{i+1} harus memiliki 'database_config'")
        
        # Validate template directory
        if 'template_directory' in config:
            template_dir = config['template_directory']
            if not isinstance(template_dir, str):
                errors.append("Template directory harus berupa string")
            elif not Path(template_dir).exists():
                errors.append(f"Template directory '{template_dir}' tidak ada")
        
        # Validate default output directory
        if 'default_output_directory' in config:
            output_dir = config['default_output_directory']
            if not isinstance(output_dir, str):
                errors.append("Default output directory harus berupa string")
            else:
                try:
                    output_path = Path(output_dir)
                    if not output_path.parent.exists():
                        errors.append(f"Parent directory dari '{output_dir}' tidak ada")
                except Exception as e:
                    errors.append(f"Default output directory tidak valid: {str(e)}")
        
        return len(errors) == 0, errors
    
    def validate_file_path(self, file_path: str, must_exist: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate file path
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must exist
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not file_path:
            errors.append("Path file tidak boleh kosong")
            return False, errors
        
        try:
            path_obj = Path(file_path)
            
            # Check if parent directory exists
            if not path_obj.parent.exists():
                errors.append(f"Direktori parent '{path_obj.parent}' tidak ada")
            
            # Check if file must exist
            if must_exist and not path_obj.exists():
                errors.append(f"File '{file_path}' tidak ditemukan")
            
            # Check file extension for known types
            if path_obj.suffix:
                known_extensions = {'.json', '.pdf', '.xlsx', '.csv', '.txt', '.log'}
                if path_obj.suffix.lower() not in known_extensions:
                    # This is a warning, not an error
                    self.logger.warning(f"Unknown file extension: {path_obj.suffix}")
            
        except Exception as e:
            errors.append(f"Path file tidak valid: {str(e)}")
        
        return len(errors) == 0, errors
    
    def get_validation_summary(self, month: str, estates: List[str], 
                             template: Optional[ReportTemplate],
                             export_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive validation summary
        
        Args:
            month: Selected month
            estates: Selected estates
            template: Selected template
            export_settings: Export settings
            
        Returns:
            Validation summary dictionary
        """
        summary = {
            'overall_valid': True,
            'total_errors': 0,
            'total_warnings': 0,
            'validations': {}
        }
        
        # Validate each component
        components = [
            ('month', lambda: self.validate_month_selection(month)),
            ('estates', lambda: self.validate_estate_selection(estates)),
            ('template', lambda: self.validate_template_selection(template)),
            ('export_settings', lambda: self.validate_export_settings(export_settings))
        ]
        
        for component_name, validator in components:
            try:
                is_valid, errors = validator()
                summary['validations'][component_name] = {
                    'valid': is_valid,
                    'errors': errors,
                    'error_count': len(errors)
                }
                
                if not is_valid:
                    summary['overall_valid'] = False
                    summary['total_errors'] += len(errors)
                    
            except Exception as e:
                summary['validations'][component_name] = {
                    'valid': False,
                    'errors': [f"Validation error: {str(e)}"],
                    'error_count': 1
                }
                summary['overall_valid'] = False
                summary['total_errors'] += 1
        
        return summary