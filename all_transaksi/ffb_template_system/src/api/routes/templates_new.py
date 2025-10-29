"""
FFB Template API Routes - Template-based Report Generation
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
from pathlib import Path

from ...core.templates.template_engine import FFRTemplateEngine
from ...core.database.connection import MultiEstateConnectionManager, create_multi_estate_manager
from ...app import get_multi_estate_manager

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates_v2', __name__, url_prefix='/templates')


def get_template_engine() -> FFRTemplateEngine:
    """Get template engine instance"""
    multi_estate_manager = get_multi_estate_manager()
    if not multi_estate_manager:
        raise Exception("Multi-estate manager not initialized")
    return FFRTemplateEngine(multi_estate_manager)


@templates_bp.route('', methods=['GET'])
def list_templates():
    """List all available templates"""
    try:
        engine = get_template_engine()
        templates = engine.list_templates()

        return jsonify({
            'success': True,
            'data': templates,
            'total': len(templates),
            'message': f'Found {len(templates)} templates'
        })
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to list templates'
        }), 500


@templates_bp.route('/<template_name>', methods=['GET'])
def get_template_info(template_name: str):
    """Get detailed information about a specific template"""
    try:
        engine = get_template_engine()

        # Try to find template file
        template_file = f"{template_name}.json"
        if not Path("templates").joinpath(template_file).exists():
            # Try with .json extension if not provided
            if not template_name.endswith('.json'):
                template_file = f"{template_name}.json"

        template_info = engine.get_template_info(template_file)

        if template_info:
            return jsonify({
                'success': True,
                'data': template_info,
                'message': f'Template {template_name} loaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Template {template_name} not found',
                'message': 'Template not found'
            }), 404

    except Exception as e:
        logger.error(f"Error getting template info for {template_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to get template info'
        }), 500


@templates_bp.route('/<template_name>/execute', methods=['POST'])
def execute_template(template_name: str):
    """Execute template with parameters"""
    try:
        # Get request data
        data = request.get_json() or {}
        parameters = data.get('parameters', {})
        estates = data.get('estates', [])

        # Validate required parameters
        if not parameters:
            return jsonify({
                'success': False,
                'error': 'No parameters provided',
                'message': 'Parameters are required for template execution'
            }), 400

        # Get template engine
        engine = get_template_engine()

        # Find template file
        template_file = f"{template_name}.json"
        if not Path("templates").joinpath(template_file).exists():
            if not template_name.endswith('.json'):
                template_file = f"{template_name}.json"

        # Execute template
        result = engine.execute_template(template_file, parameters, estates)

        # Return execution result
        status_code = 200 if result['success'] else 400
        return jsonify({
            'success': result['success'],
            'data': result.get('data', []),
            'total_records': result.get('total_records', 0),
            'estates_processed': result.get('estates_processed', 0),
            'report_files': result.get('report_files', []),
            'errors': result.get('errors', []),
            'execution_time': result.get('execution_time'),
            'message': result.get('message', 'Template execution completed')
        }), status_code

    except Exception as e:
        logger.error(f"Error executing template {template_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to execute template {template_name}'
        }), 500


@templates_bp.route('/<template_name>/preview', methods=['POST'])
def preview_template(template_name: str):
    """Preview template with sample data (limited records)"""
    try:
        # Get request data
        data = request.get_json() or {}
        parameters = data.get('parameters', {})
        estates = data.get('estates', [])
        limit = data.get('limit', 10)  # Limit preview to 10 records

        # Modify parameters for preview
        preview_params = parameters.copy()
        preview_params['PREVIEW_MODE'] = True
        preview_params['RECORD_LIMIT'] = limit

        # Get template engine and execute
        engine = get_template_engine()

        template_file = f"{template_name}.json"
        if not Path("templates").joinpath(template_file).exists():
            if not template_name.endswith('.json'):
                template_file = f"{template_name}.json"

        result = engine.execute_template(template_file, preview_params, estates)

        # Return preview result (limited data)
        if result['success']:
            preview_data = result.get('data', [])[:limit]
            return jsonify({
                'success': True,
                'data': preview_data,
                'preview_records': len(preview_data),
                'total_available': result.get('total_records', 0),
                'message': f'Preview generated with {len(preview_data)} records'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('errors', ['Preview failed']),
                'message': 'Preview generation failed'
            }), 400

    except Exception as e:
        logger.error(f"Error previewing template {template_name}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to preview template {template_name}'
        }), 500


@templates_bp.route('/categories', methods=['GET'])
def get_template_categories():
    """Get available template categories"""
    try:
        categories = {
            "KINERJA_KARYAWAN": "Laporan Kinerja Karyawan",
            "FFB_ANALYSIS": "FFB Transaction Analysis",
            "DATA_QUALITY": "Data Quality Report",
            "SUMMARY": "Executive Summary",
            "PERFORMANCE": "Performance Analysis",
            "COMPLIANCE": "Compliance Reports"
        }

        return jsonify({
            'success': True,
            'data': categories,
            'total': len(categories),
            'message': 'Template categories retrieved successfully'
        })

    except Exception as e:
        logger.error(f"Error getting template categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get template categories'
        }), 500


@templates_bp.route('/validate', methods=['POST'])
def validate_parameters():
    """Validate template parameters"""
    try:
        data = request.get_json() or {}
        template_name = data.get('template_name')
        parameters = data.get('parameters', {})

        if not template_name:
            return jsonify({
                'success': False,
                'error': 'Template name is required',
                'message': 'Template name must be provided'
            }), 400

        # Get template engine and template info
        engine = get_template_engine()

        template_file = f"{template_name}.json"
        if not Path("templates").joinpath(template_file).exists():
            if not template_name.endswith('.json'):
                template_file = f"{template_name}.json"

        template = engine.load_template(template_file)

        # Validate parameters
        is_valid, errors = engine.validate_parameters(template, parameters)

        return jsonify({
            'success': is_valid,
            'valid': is_valid,
            'errors': errors,
            'message': 'Parameters are valid' if is_valid else f'Validation failed: {", ".join(errors)}'
        })

    except Exception as e:
        logger.error(f"Error validating parameters: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Parameter validation failed'
        }), 500


@templates_bp.route('/reports/download/<filename>', methods=['GET'])
def download_report(filename: str):
    """Download generated report file"""
    try:
        reports_dir = Path("reports")
        file_path = reports_dir / filename

        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found',
                'message': f'Report file {filename} not found'
            }), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        logger.error(f"Error downloading report {filename}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to download report {filename}'
        }), 500


@templates_bp.route('/reports', methods=['GET'])
def list_reports():
    """List all generated reports"""
    try:
        reports_dir = Path("reports")
        if not reports_dir.exists():
            return jsonify({
                'success': True,
                'data': [],
                'total': 0,
                'message': 'No reports directory found'
            })

        reports = []
        for file_path in reports_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                reports.append({
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'download_url': f'/api/templates/reports/download/{file_path.name}'
                })

        # Sort by modified date (newest first)
        reports.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'data': reports,
            'total': len(reports),
            'message': f'Found {len(reports)} report files'
        })

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to list reports'
        }), 500


# Template management endpoints
@templates_bp.route('/upload', methods=['POST'])
def upload_template():
    """Upload new template file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'message': 'Template file is required'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a template file'
            }), 400

        # Save template file
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)

        filename = file.filename
        file_path = templates_dir / filename
        file.save(file_path)

        # Validate template format
        try:
            engine = get_template_engine()
            template_info = engine.get_template_info(filename)

            return jsonify({
                'success': True,
                'data': {
                    'filename': filename,
                    'template_info': template_info
                },
                'message': f'Template {filename} uploaded successfully'
            })
        except Exception as e:
            # Remove invalid file
            if file_path.exists():
                file_path.unlink()

            return jsonify({
                'success': False,
                'error': f'Invalid template format: {str(e)}',
                'message': 'Uploaded file is not a valid template'
            }), 400

    except Exception as e:
        logger.error(f"Error uploading template: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to upload template'
        }), 500


@templates_bp.route('/health', methods=['GET'])
def template_health_check():
    """Template engine health check"""
    try:
        multi_estate_manager = get_multi_estate_manager()

        health_status = {
            'template_engine': 'available',
            'multi_estate_manager': 'available' if multi_estate_manager else 'unavailable',
            'template_directory': 'available' if Path("templates").exists() else 'unavailable',
            'reports_directory': 'available' if Path("reports").exists() else 'unavailable',
            'estates_available': len(multi_estate_manager.get_available_estates()) if multi_estate_manager else 0
        }

        overall_status = 'healthy' if all(status == 'available' for status in health_status.values() if status != 'estates_available') else 'degraded'

        return jsonify({
            'success': True,
            'status': overall_status,
            'details': health_status,
            'message': f'Template system is {overall_status}'
        })

    except Exception as e:
        logger.error(f"Template health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Template system health check failed'
        }), 500