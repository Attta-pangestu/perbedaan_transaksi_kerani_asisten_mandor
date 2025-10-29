"""
Template Service
Handles template loading, validation, and management
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from business.models.report_template import ReportTemplate
from infrastructure.exceptions.custom_exceptions import (
    TemplateNotFoundError,
    TemplateValidationError,
    TemplateLoadError
)


class TemplateService:
    """
    Service for managing report templates
    """
    
    def __init__(self, template_directory: str = None):
        """
        Initialize template service
        
        Args:
            template_directory: Base directory containing templates
        """
        if template_directory is None:
            template_directory = os.path.join(os.getcwd(), "templates")
        
        self.template_directory = Path(template_directory)
        self.logger = logging.getLogger(__name__)
        self._template_cache: Dict[str, ReportTemplate] = {}
        
        # Create template directory if it doesn't exist
        os.makedirs(self.template_directory, exist_ok=True)
    
    def get_available_templates(self) -> List[ReportTemplate]:
        """
        Get all available templates
        
        Returns:
            List of available ReportTemplate instances
            
        Raises:
            TemplateLoadError: If templates cannot be loaded
        """
        templates = []
        
        try:
            # Search for JSON template files recursively
            for template_file in self.template_directory.rglob("*.json"):
                try:
                    template = self.load_template_from_file(str(template_file))
                    if template and template.is_valid():
                        templates.append(template)
                        self.logger.debug(f"Loaded template: {template.name}")
                    else:
                        self.logger.warning(f"Invalid template skipped: {template_file}")
                        
                except Exception as e:
                    self.logger.error(f"Error loading template {template_file}: {e}")
                    continue
                    
            self.logger.info(f"Loaded {len(templates)} valid templates")
            return templates
            
        except Exception as e:
            raise TemplateLoadError(f"Failed to load templates: {e}")
    
    def load_template_from_file(self, file_path: str) -> Optional[ReportTemplate]:
        """
        Load template from file
        
        Args:
            file_path: Path to template file
            
        Returns:
            ReportTemplate instance or None if loading fails
            
        Raises:
            TemplateNotFoundError: If template file doesn't exist
            TemplateLoadError: If template cannot be loaded
        """
        if not os.path.exists(file_path):
            raise TemplateNotFoundError(f"Template file not found: {file_path}")
        
        # Check cache first
        cache_key = os.path.abspath(file_path)
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        try:
            template = ReportTemplate.from_json_file(file_path)
            
            # Cache the template
            self._template_cache[cache_key] = template
            
            self.logger.debug(f"Template loaded from {file_path}: {template.name}")
            return template
            
        except Exception as e:
            raise TemplateLoadError(f"Failed to load template from {file_path}: {e}")
    
    def get_template_by_name(self, name: str) -> Optional[ReportTemplate]:
        """
        Get template by name
        
        Args:
            name: Template name
            
        Returns:
            ReportTemplate instance or None if not found
        """
        templates = self.get_available_templates()
        
        for template in templates:
            if template.name == name:
                return template
                
        return None
    
    def get_template_by_id(self, template_id: str) -> Optional[ReportTemplate]:
        """
        Get template by ID
        
        Args:
            template_id: Template ID
            
        Returns:
            ReportTemplate instance or None if not found
        """
        templates = self.get_available_templates()
        
        for template in templates:
            if template.template_id == template_id:
                return template
                
        return None
    
    def validate_template(self, template: ReportTemplate) -> List[str]:
        """
        Validate template configuration
        
        Args:
            template: Template to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = template.validate()
        
        # Additional business logic validation
        if template.data_processing:
            # Validate query logic
            query_logic = template.data_processing.get('query_logic', {})
            if not query_logic:
                errors.append("Template must define query logic")
            
            # Validate required fields
            required_fields = template.get_required_parameters()
            if not required_fields:
                errors.append("Template must define required parameters")
        
        # Validate UI flow
        if template.ui_flow:
            startup_sequence = template.ui_flow.get('startup_sequence', [])
            if not startup_sequence:
                errors.append("Template must define startup sequence")
        
        return errors
    
    def is_template_valid(self, template: ReportTemplate) -> bool:
        """
        Check if template is valid
        
        Args:
            template: Template to validate
            
        Returns:
            True if template is valid
        """
        return len(self.validate_template(template)) == 0
    
    def get_templates_by_tag(self, tag: str) -> List[ReportTemplate]:
        """
        Get templates by tag
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of templates with the specified tag
        """
        templates = self.get_available_templates()
        
        return [
            template for template in templates
            if template.tags and tag in template.tags
        ]
    
    def search_templates(self, query: str) -> List[ReportTemplate]:
        """
        Search templates by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        templates = self.get_available_templates()
        query_lower = query.lower()
        
        matching_templates = []
        
        for template in templates:
            # Search in name
            if query_lower in template.name.lower():
                matching_templates.append(template)
                continue
                
            # Search in description
            if query_lower in template.description.lower():
                matching_templates.append(template)
                continue
                
            # Search in tags
            if template.tags:
                for tag in template.tags:
                    if query_lower in tag.lower():
                        matching_templates.append(template)
                        break
        
        return matching_templates
    
    def get_template_summary(self) -> Dict[str, Any]:
        """
        Get summary of available templates
        
        Returns:
            Dictionary with template summary information
        """
        templates = self.get_available_templates()
        
        summary = {
            'total_templates': len(templates),
            'templates': [],
            'tags': set(),
            'formats': set()
        }
        
        for template in templates:
            template_info = {
                'name': template.name,
                'description': template.description,
                'version': template.version,
                'template_id': template.template_id,
                'tags': template.tags or [],
                'supported_formats': template.get_supported_formats(),
                'multi_estate_support': template.supports_multi_estate()
            }
            
            summary['templates'].append(template_info)
            
            # Collect tags
            if template.tags:
                summary['tags'].update(template.tags)
                
            # Collect formats
            summary['formats'].update(template.get_supported_formats())
        
        # Convert sets to lists for JSON serialization
        summary['tags'] = list(summary['tags'])
        summary['formats'] = list(summary['formats'])
        
        return summary
    
    def clear_cache(self):
        """Clear template cache"""
        self._template_cache.clear()
        self.logger.debug("Template cache cleared")
    
    def reload_templates(self):
        """Reload all templates (clear cache and reload)"""
        self.clear_cache()
        templates = self.get_available_templates()
        self.logger.info(f"Reloaded {len(templates)} templates")
        return templates
    
    def get_default_template(self) -> Optional[ReportTemplate]:
        """
        Get default template (first valid template found)
        
        Returns:
            Default ReportTemplate or None if no templates available
        """
        templates = self.get_available_templates()
        
        if templates:
            return templates[0]
            
        return None
    
    def export_template_config(self, template: ReportTemplate, output_path: str):
        """
        Export template configuration to file
        
        Args:
            template: Template to export
            output_path: Output file path
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            config_data = template.to_dict()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Template config exported to {output_path}")
            
        except Exception as e:
            raise IOError(f"Failed to export template config: {e}")
    
    def __str__(self) -> str:
        """String representation"""
        return f"TemplateService(directory='{self.template_directory}')"