"""
Web Routes Package Initialization
"""

from flask import Blueprint, render_template

# Create web blueprint
web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@web_bp.route('/templates')
def templates():
    """Templates management page"""
    return render_template('template_editor.html')


@web_bp.route('/reports')
def reports():
    """Reports management page"""
    return render_template('reports.html')


@web_bp.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'FFB Template System is running'}


__all__ = ['web_bp']