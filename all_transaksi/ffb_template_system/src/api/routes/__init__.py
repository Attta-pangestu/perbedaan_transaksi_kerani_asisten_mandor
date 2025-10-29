"""
API Routes Package Initialization
"""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import all route modules
from . import templates
from . import reports
from . import templates_new

# Register sub-blueprints
api_bp.register_blueprint(templates.templates_bp, url_prefix='/templates_old')
api_bp.register_blueprint(templates_new.templates_bp, url_prefix='/templates')
api_bp.register_blueprint(reports.reports_bp, url_prefix='/reports')

__all__ = ['api_bp']