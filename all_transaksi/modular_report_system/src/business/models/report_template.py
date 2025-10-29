"""
Report Template Domain Model
Represents a report template with its configuration and metadata
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


@dataclass
class ReportTemplate:
    """
    Domain model for report templates
    """
    
    # Template identification
    name: str
    description: str
    version: str
    template_id: str
    
    # Template configuration
    config: Dict[str, Any]
    
    # UI flow configuration
    ui_flow: Dict[str, Any]
    
    # Data processing configuration
    data_processing: Dict[str, Any]
    
    # Report formatting configuration
    report_format: Dict[str, Any]
    
    # Template metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # File information
    file_path: Optional[str] = None
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'ReportTemplate':
        """
        Create ReportTemplate instance from JSON file
        
        Args:
            file_path: Path to the template JSON file
            
        Returns:
            ReportTemplate instance
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If required fields are missing
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract template data from the nested structure
            template_data = data.get('ffb_verification_report_template', {})
            
            if not template_data:
                raise ValueError(f"Invalid template structure in {file_path}")
                
            return cls(
                name=template_data.get('name', ''),
                description=template_data.get('description', ''),
                version=template_data.get('version', '1.0'),
                template_id=template_data.get('template_id', file_path),
                config=template_data,
                ui_flow=template_data.get('ui_flow', {}),
                data_processing=template_data.get('data_processing', {}),
                report_format=template_data.get('report_format', {}),
                file_path=file_path,
                tags=template_data.get('tags', [])
            )
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in template file {file_path}: {e}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], file_path: Optional[str] = None) -> 'ReportTemplate':
        """
        Create ReportTemplate instance from dictionary
        
        Args:
            data: Template data dictionary
            file_path: Optional file path
            
        Returns:
            ReportTemplate instance
        """
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            version=data.get('version', '1.0'),
            template_id=data.get('template_id', ''),
            config=data,
            ui_flow=data.get('ui_flow', {}),
            data_processing=data.get('data_processing', {}),
            report_format=data.get('report_format', {}),
            file_path=file_path,
            tags=data.get('tags', [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ReportTemplate to dictionary
        
        Returns:
            Dictionary representation of the template
        """
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'template_id': self.template_id,
            'config': self.config,
            'ui_flow': self.ui_flow,
            'data_processing': self.data_processing,
            'report_format': self.report_format,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author,
            'tags': self.tags,
            'file_path': self.file_path
        }
    
    def validate(self) -> List[str]:
        """
        Validate template configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields validation
        if not self.name:
            errors.append("Template name is required")
        
        if not self.description:
            errors.append("Template description is required")
            
        if not self.template_id:
            errors.append("Template ID is required")
        
        # Configuration validation
        if not isinstance(self.config, dict):
            errors.append("Template config must be a dictionary")
        
        # UI flow validation
        if self.ui_flow and not isinstance(self.ui_flow, dict):
            errors.append("UI flow must be a dictionary")
            
        # Data processing validation
        if self.data_processing and not isinstance(self.data_processing, dict):
            errors.append("Data processing config must be a dictionary")
            
        # Report format validation
        if self.report_format and not isinstance(self.report_format, dict):
            errors.append("Report format config must be a dictionary")
        
        return errors
    
    def is_valid(self) -> bool:
        """
        Check if template is valid
        
        Returns:
            True if template is valid, False otherwise
        """
        return len(self.validate()) == 0
    
    def get_supported_formats(self) -> List[str]:
        """
        Get supported export formats for this template
        
        Returns:
            List of supported formats
        """
        formats = self.report_format.get('supported_formats', ['PDF'])
        return formats if isinstance(formats, list) else ['PDF']
    
    def get_required_parameters(self) -> List[str]:
        """
        Get required parameters for this template
        
        Returns:
            List of required parameter names
        """
        params = self.data_processing.get('required_parameters', [])
        return params if isinstance(params, list) else []
    
    def supports_multi_estate(self) -> bool:
        """
        Check if template supports multi-estate processing
        
        Returns:
            True if multi-estate is supported
        """
        return self.config.get('multi_estate_support', True)
    
    def __str__(self) -> str:
        """String representation of the template"""
        return f"ReportTemplate(name='{self.name}', version='{self.version}')"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"ReportTemplate(name='{self.name}', description='{self.description}', "
                f"version='{self.version}', template_id='{self.template_id}')")