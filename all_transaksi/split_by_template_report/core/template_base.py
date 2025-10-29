"""
Base Template System for FFB Analysis Application

This module provides the abstract base class and interfaces for creating
customizable templates in the FFB analysis system.

Author: Generated for Modular FFB Analysis System
Date: 2024
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import json
import os
from datetime import datetime
import pandas as pd


class TemplateConfigInterface(ABC):
    """Abstract interface for template configuration"""
    
    @abstractmethod
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load template configuration from file"""
        pass
    
    @abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        pass


class TemplateGUIInterface(ABC):
    """Abstract interface for template GUI components"""
    
    @abstractmethod
    def create_template_frame(self, parent) -> Any:
        """Create template-specific GUI frame"""
        pass
    
    @abstractmethod
    def get_template_inputs(self) -> Dict[str, Any]:
        """Get user inputs from template GUI"""
        pass
    
    @abstractmethod
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate user inputs, return (is_valid, error_message)"""
        pass
    
    @abstractmethod
    def reset_inputs(self) -> None:
        """Reset all input fields to default values"""
        pass


class TemplateBusinessLogicInterface(ABC):
    """Abstract interface for template business logic"""
    
    @abstractmethod
    def process_data(self, raw_data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Process raw data according to template logic"""
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Validate processed data"""
        pass
    
    @abstractmethod
    def generate_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics from processed data"""
        pass


class TemplateReportInterface(ABC):
    """Abstract interface for template report generation"""
    
    @abstractmethod
    def generate_excel_report(self, data: pd.DataFrame, output_path: str, config: Dict[str, Any]) -> bool:
        """Generate Excel report"""
        pass
    
    @abstractmethod
    def generate_pdf_report(self, data: pd.DataFrame, output_path: str, config: Dict[str, Any]) -> bool:
        """Generate PDF report"""
        pass
    
    @abstractmethod
    def get_report_filename(self, config: Dict[str, Any]) -> str:
        """Generate appropriate filename for reports"""
        pass


class BaseTemplate(ABC):
    """
    Abstract base class for all FFB analysis templates.
    
    This class defines the common interface and provides shared functionality
    for all templates in the system.
    """
    
    def __init__(self, template_name: str, template_path: str):
        """
        Initialize base template
        
        Args:
            template_name: Unique name for the template
            template_path: Path to template directory
        """
        self.template_name = template_name
        self.template_path = template_path
        self.config_path = os.path.join(template_path, "config.json")
        self.config = {}
        self.is_initialized = False
        
        # Initialize components
        self._config_handler = None
        self._gui_handler = None
        self._business_logic = None
        self._report_generator = None
    
    @abstractmethod
    def initialize_template(self) -> bool:
        """
        Initialize template components and configuration
        
        Returns:
            bool: True if initialization successful
        """
        pass
    
    @abstractmethod
    def get_config_handler(self) -> TemplateConfigInterface:
        """Get template configuration handler"""
        pass
    
    @abstractmethod
    def get_gui_handler(self) -> TemplateGUIInterface:
        """Get template GUI handler"""
        pass
    
    @abstractmethod
    def get_business_logic(self) -> TemplateBusinessLogicInterface:
        """Get template business logic handler"""
        pass
    
    @abstractmethod
    def get_report_generator(self) -> TemplateReportInterface:
        """Get template report generator"""
        pass
    
    def get_template_info(self) -> Dict[str, Any]:
        """
        Get template information
        
        Returns:
            Dict containing template metadata
        """
        return {
            "name": self.template_name,
            "path": self.template_path,
            "config_path": self.config_path,
            "is_initialized": self.is_initialized,
            "version": self.config.get("version", "1.0.0"),
            "description": self.config.get("description", ""),
            "author": self.config.get("author", ""),
            "created_date": self.config.get("created_date", "")
        }
    
    def load_base_config(self) -> bool:
        """
        Load base configuration common to all templates
        
        Returns:
            bool: True if configuration loaded successfully
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                return True
            else:
                print(f"Warning: Configuration file not found at {self.config_path}")
                return False
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return False
    
    def validate_template_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate template directory structure and required files
        
        Returns:
            Tuple of (is_valid, list_of_missing_items)
        """
        missing_items = []
        
        # Check if template directory exists
        if not os.path.exists(self.template_path):
            missing_items.append(f"Template directory: {self.template_path}")
        
        # Check for required files
        required_files = [
            "config.json",
            "__init__.py"
        ]
        
        for file_name in required_files:
            file_path = os.path.join(self.template_path, file_name)
            if not os.path.exists(file_path):
                missing_items.append(f"Required file: {file_name}")
        
        return len(missing_items) == 0, missing_items
    
    def execute_analysis(self, database_connector, analysis_params: Dict[str, Any]) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Execute complete analysis workflow for this template
        
        Args:
            database_connector: Database connector instance
            analysis_params: Parameters for analysis
            
        Returns:
            Tuple of (success, message, processed_data)
        """
        try:
            # Validate inputs
            gui_handler = self.get_gui_handler()
            is_valid, error_msg = gui_handler.validate_inputs()
            if not is_valid:
                return False, f"Input validation failed: {error_msg}", None
            
            # Get template inputs
            template_inputs = gui_handler.get_template_inputs()
            
            # Execute database query (this should be implemented by specific templates)
            raw_data = self._execute_database_query(database_connector, template_inputs, analysis_params)
            if raw_data is None or raw_data.empty:
                return False, "No data retrieved from database", None
            
            # Process data using business logic
            business_logic = self.get_business_logic()
            processed_data = business_logic.process_data(raw_data, self.config)
            
            # Validate processed data
            is_valid, error_msg = business_logic.validate_data(processed_data)
            if not is_valid:
                return False, f"Data validation failed: {error_msg}", None
            
            return True, "Analysis completed successfully", processed_data
            
        except Exception as e:
            return False, f"Analysis execution failed: {str(e)}", None
    
    @abstractmethod
    def _execute_database_query(self, database_connector, template_inputs: Dict[str, Any], analysis_params: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Execute database query specific to this template
        
        Args:
            database_connector: Database connector instance
            template_inputs: Inputs from template GUI
            analysis_params: General analysis parameters
            
        Returns:
            DataFrame with raw data or None if failed
        """
        pass
    
    def generate_reports(self, data: pd.DataFrame, output_directory: str) -> Tuple[bool, str]:
        """
        Generate all reports for this template
        
        Args:
            data: Processed data to generate reports from
            output_directory: Directory to save reports
            
        Returns:
            Tuple of (success, message)
        """
        try:
            report_generator = self.get_report_generator()
            
            # Generate filename
            filename = report_generator.get_report_filename(self.config)
            
            # Generate Excel report
            excel_path = os.path.join(output_directory, f"{filename}.xlsx")
            excel_success = report_generator.generate_excel_report(data, excel_path, self.config)
            
            # Generate PDF report
            pdf_path = os.path.join(output_directory, f"{filename}.pdf")
            pdf_success = report_generator.generate_pdf_report(data, pdf_path, self.config)
            
            if excel_success and pdf_success:
                return True, f"Reports generated successfully: {filename}"
            elif excel_success:
                return True, f"Excel report generated successfully: {filename}.xlsx (PDF generation failed)"
            elif pdf_success:
                return True, f"PDF report generated successfully: {filename}.pdf (Excel generation failed)"
            else:
                return False, "Both report generations failed"
                
        except Exception as e:
            return False, f"Report generation failed: {str(e)}"


class TemplateRegistry:
    """Registry for managing available templates"""
    
    def __init__(self):
        self._templates = {}
        self._template_paths = {}
    
    def register_template(self, template_class: type, template_name: str, template_path: str) -> bool:
        """
        Register a template class
        
        Args:
            template_class: Template class that inherits from BaseTemplate
            template_name: Unique name for the template
            template_path: Path to template directory
            
        Returns:
            bool: True if registration successful
        """
        try:
            if not issubclass(template_class, BaseTemplate):
                raise ValueError("Template class must inherit from BaseTemplate")
            
            self._templates[template_name] = template_class
            self._template_paths[template_name] = template_path
            return True
            
        except Exception as e:
            print(f"Failed to register template {template_name}: {str(e)}")
            return False
    
    def get_template(self, template_name: str) -> Optional[BaseTemplate]:
        """
        Get template instance by name
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template instance or None if not found
        """
        if template_name in self._templates:
            template_class = self._templates[template_name]
            template_path = self._template_paths[template_name]
            return template_class(template_name, template_path)
        return None
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names"""
        return list(self._templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template information without instantiating"""
        if template_name in self._templates:
            template_path = self._template_paths[template_name]
            config_path = os.path.join(template_path, "config.json")
            
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    return {
                        "name": template_name,
                        "path": template_path,
                        "version": config.get("version", "1.0.0"),
                        "description": config.get("description", ""),
                        "author": config.get("author", ""),
                        "created_date": config.get("created_date", "")
                    }
            except Exception as e:
                print(f"Error reading template info for {template_name}: {str(e)}")
        
        return None


# Global template registry instance
template_registry = TemplateRegistry()