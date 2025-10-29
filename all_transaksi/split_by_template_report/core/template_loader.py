"""
Dynamic Template Loader for FFB Analysis Application

This module provides functionality to dynamically discover, load, and manage
templates in the FFB analysis system.

Author: Generated for Modular FFB Analysis System
Date: 2024
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path

from .template_base import BaseTemplate, template_registry


class TemplateLoader:
    """
    Dynamic template loader that discovers and loads templates from the templates directory
    """
    
    def __init__(self, templates_base_path: str):
        """
        Initialize template loader
        
        Args:
            templates_base_path: Base path where template directories are located
        """
        self.templates_base_path = templates_base_path
        self.loaded_templates = {}
        self.template_errors = {}
        
    def discover_templates(self) -> List[str]:
        """
        Discover all available templates in the templates directory
        
        Returns:
            List of template directory names
        """
        templates = []
        
        if not os.path.exists(self.templates_base_path):
            print(f"Templates base path does not exist: {self.templates_base_path}")
            return templates
        
        try:
            for item in os.listdir(self.templates_base_path):
                item_path = os.path.join(self.templates_base_path, item)
                
                # Check if it's a directory and contains required files
                if os.path.isdir(item_path):
                    if self._is_valid_template_directory(item_path):
                        templates.append(item)
                    else:
                        print(f"Invalid template directory structure: {item}")
                        
        except Exception as e:
            print(f"Error discovering templates: {str(e)}")
        
        return templates
    
    def _is_valid_template_directory(self, template_path: str) -> bool:
        """
        Check if a directory is a valid template directory
        
        Args:
            template_path: Path to template directory
            
        Returns:
            bool: True if valid template directory
        """
        required_files = [
            "config.json",
            "__init__.py",
            "template.py"
        ]
        
        for file_name in required_files:
            file_path = os.path.join(template_path, file_name)
            if not os.path.exists(file_path):
                return False
        
        # Validate config.json structure
        try:
            config_path = os.path.join(template_path, "config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_config_keys = ["name", "version", "template_class"]
            for key in required_config_keys:
                if key not in config:
                    print(f"Missing required config key '{key}' in {config_path}")
                    return False
                    
        except Exception as e:
            print(f"Error validating config.json in {template_path}: {str(e)}")
            return False
        
        return True
    
    def load_template(self, template_name: str) -> Tuple[bool, str, Optional[BaseTemplate]]:
        """
        Load a specific template by name
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            Tuple of (success, message, template_instance)
        """
        template_path = os.path.join(self.templates_base_path, template_name)
        
        if not os.path.exists(template_path):
            return False, f"Template directory not found: {template_path}", None
        
        if not self._is_valid_template_directory(template_path):
            return False, f"Invalid template directory structure: {template_name}", None
        
        try:
            # Load template configuration
            config_path = os.path.join(template_path, "config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            template_class_name = config["template_class"]
            
            # Import template module
            module_path = os.path.join(template_path, "template.py")
            spec = importlib.util.spec_from_file_location(f"{template_name}_template", module_path)
            
            if spec is None or spec.loader is None:
                return False, f"Could not load template module: {template_name}", None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"{template_name}_template"] = module
            spec.loader.exec_module(module)
            
            # Get template class
            if not hasattr(module, template_class_name):
                return False, f"Template class '{template_class_name}' not found in module", None
            
            template_class = getattr(module, template_class_name)
            
            # Validate template class
            if not issubclass(template_class, BaseTemplate):
                return False, f"Template class must inherit from BaseTemplate", None
            
            # Create template instance
            template_instance = template_class(template_name, template_path)
            
            # Initialize template
            if not template_instance.initialize_template():
                return False, f"Template initialization failed: {template_name}", None
            
            # Register template
            template_registry.register_template(template_class, template_name, template_path)
            
            # Store loaded template
            self.loaded_templates[template_name] = template_instance
            
            return True, f"Template loaded successfully: {template_name}", template_instance
            
        except Exception as e:
            error_msg = f"Error loading template {template_name}: {str(e)}"
            self.template_errors[template_name] = error_msg
            return False, error_msg, None
    
    def load_all_templates(self) -> Dict[str, Tuple[bool, str, Optional[BaseTemplate]]]:
        """
        Load all discovered templates
        
        Returns:
            Dictionary mapping template names to (success, message, template_instance)
        """
        results = {}
        templates = self.discover_templates()
        
        for template_name in templates:
            success, message, template_instance = self.load_template(template_name)
            results[template_name] = (success, message, template_instance)
        
        return results
    
    def get_loaded_template(self, template_name: str) -> Optional[BaseTemplate]:
        """
        Get a loaded template instance
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template instance or None if not loaded
        """
        return self.loaded_templates.get(template_name)
    
    def get_loaded_templates(self) -> Dict[str, BaseTemplate]:
        """Get all loaded templates"""
        return self.loaded_templates.copy()
    
    def get_template_errors(self) -> Dict[str, str]:
        """Get template loading errors"""
        return self.template_errors.copy()
    
    def reload_template(self, template_name: str) -> Tuple[bool, str, Optional[BaseTemplate]]:
        """
        Reload a specific template (useful for development)
        
        Args:
            template_name: Name of the template to reload
            
        Returns:
            Tuple of (success, message, template_instance)
        """
        # Remove from loaded templates if exists
        if template_name in self.loaded_templates:
            del self.loaded_templates[template_name]
        
        # Remove from errors if exists
        if template_name in self.template_errors:
            del self.template_errors[template_name]
        
        # Remove from sys.modules if exists
        module_name = f"{template_name}_template"
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Load template again
        return self.load_template(template_name)
    
    def get_template_info_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all discovered templates (loaded and unloaded)
        
        Returns:
            Dictionary mapping template names to their info
        """
        info = {}
        templates = self.discover_templates()
        
        for template_name in templates:
            template_path = os.path.join(self.templates_base_path, template_name)
            config_path = os.path.join(template_path, "config.json")
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                info[template_name] = {
                    "name": template_name,
                    "path": template_path,
                    "version": config.get("version", "1.0.0"),
                    "description": config.get("description", ""),
                    "author": config.get("author", ""),
                    "created_date": config.get("created_date", ""),
                    "template_class": config.get("template_class", ""),
                    "is_loaded": template_name in self.loaded_templates,
                    "load_error": self.template_errors.get(template_name, "")
                }
                
            except Exception as e:
                info[template_name] = {
                    "name": template_name,
                    "path": template_path,
                    "error": f"Error reading config: {str(e)}",
                    "is_loaded": False
                }
        
        return info
    
    def validate_all_templates(self) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all discovered templates without loading them
        
        Returns:
            Dictionary mapping template names to (is_valid, list_of_issues)
        """
        validation_results = {}
        templates = self.discover_templates()
        
        for template_name in templates:
            template_path = os.path.join(self.templates_base_path, template_name)
            issues = []
            
            # Check directory structure
            required_files = ["config.json", "__init__.py", "template.py"]
            for file_name in required_files:
                file_path = os.path.join(template_path, file_name)
                if not os.path.exists(file_path):
                    issues.append(f"Missing required file: {file_name}")
            
            # Validate config.json
            config_path = os.path.join(template_path, "config.json")
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                required_keys = ["name", "version", "template_class", "description"]
                for key in required_keys:
                    if key not in config:
                        issues.append(f"Missing required config key: {key}")
                
                # Check if template name matches directory name
                if config.get("name") != template_name:
                    issues.append(f"Template name in config ({config.get('name')}) doesn't match directory name ({template_name})")
                        
            except json.JSONDecodeError as e:
                issues.append(f"Invalid JSON in config.json: {str(e)}")
            except Exception as e:
                issues.append(f"Error reading config.json: {str(e)}")
            
            validation_results[template_name] = (len(issues) == 0, issues)
        
        return validation_results


class TemplateManager:
    """
    High-level template manager that combines loading and registry functionality
    """
    
    def __init__(self, templates_base_path: str):
        """
        Initialize template manager
        
        Args:
            templates_base_path: Base path where template directories are located
        """
        self.loader = TemplateLoader(templates_base_path)
        self.templates_base_path = templates_base_path
    
    def initialize(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Initialize template manager by loading all templates
        
        Returns:
            Tuple of (success, message, load_results)
        """
        try:
            load_results = self.loader.load_all_templates()
            
            successful_loads = sum(1 for success, _, _ in load_results.values() if success)
            total_templates = len(load_results)
            
            if successful_loads == 0:
                return False, "No templates loaded successfully", load_results
            elif successful_loads < total_templates:
                return True, f"Partially successful: {successful_loads}/{total_templates} templates loaded", load_results
            else:
                return True, f"All templates loaded successfully: {successful_loads}/{total_templates}", load_results
                
        except Exception as e:
            return False, f"Template manager initialization failed: {str(e)}", {}
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names"""
        return list(self.loader.get_loaded_templates().keys())
    
    def get_template(self, template_name: str) -> Optional[BaseTemplate]:
        """Get template instance by name"""
        return self.loader.get_loaded_template(template_name)
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template information"""
        all_info = self.loader.get_template_info_all()
        return all_info.get(template_name)
    
    def get_all_template_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all templates"""
        return self.loader.get_template_info_all()
    
    def reload_template(self, template_name: str) -> Tuple[bool, str]:
        """Reload a specific template"""
        success, message, _ = self.loader.reload_template(template_name)
        return success, message
    
    def reload_templates(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Reload all templates
        
        Returns:
            Tuple of (success, message, load_results)
        """
        try:
            # Clear existing loaded templates
            self.loader.loaded_templates.clear()
            self.loader.template_errors.clear()
            
            # Reload all templates
            load_results = self.loader.load_all_templates()
            
            successful_loads = sum(1 for success, _, _ in load_results.values() if success)
            total_templates = len(load_results)
            
            if successful_loads == 0:
                return False, "No templates reloaded successfully", load_results
            elif successful_loads < total_templates:
                return True, f"Partially successful: {successful_loads}/{total_templates} templates reloaded", load_results
            else:
                return True, f"All templates reloaded successfully: {successful_loads}/{total_templates}", load_results
                
        except Exception as e:
            return False, f"Template reload failed: {str(e)}", {}
    
    def validate_templates(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all templates"""
        return self.loader.validate_all_templates()