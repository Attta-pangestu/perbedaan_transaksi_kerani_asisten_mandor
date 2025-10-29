"""
Core module for FFB Analysis Modular System

This module provides the core functionality for the modular FFB analysis system,
including database connectivity, template system, and dynamic loading capabilities.

Author: Generated for Modular FFB Analysis System
Date: 2024
"""

from .database_connector import (
    DatabaseConnectorInterface,
    FirebirdModularConnector,
    DatabaseConnectorFactory,
    DatabaseConfig
)

from .template_base import (
    BaseTemplate,
    TemplateConfigInterface,
    TemplateGUIInterface,
    TemplateBusinessLogicInterface,
    TemplateReportInterface,
    TemplateRegistry,
    template_registry
)

from .template_loader import (
    TemplateLoader,
    TemplateManager
)

__version__ = "1.0.0"
__author__ = "Generated for Modular FFB Analysis System"

__all__ = [
    # Database components
    "DatabaseConnectorInterface",
    "FirebirdModularConnector", 
    "DatabaseConnectorFactory",
    "DatabaseConfig",
    
    # Template system components
    "BaseTemplate",
    "TemplateConfigInterface",
    "TemplateGUIInterface", 
    "TemplateBusinessLogicInterface",
    "TemplateReportInterface",
    "TemplateRegistry",
    "template_registry",
    
    # Template loading components
    "TemplateLoader",
    "TemplateManager"
]