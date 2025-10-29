"""
Template API Routes
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import tempfile
import os
from datetime import datetime

from ...core.templates.template_service import TemplateService
from ...core.database.repositories import ReportTemplateRepository
from ...core.database.connection import get_database_session
from ...core.reports.jasper_service import JasperReportService
from ...app import get_multi_estate_manager

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

@templates_bp.route('', methods=['GET'])
def get_templates():
    """Get all templates"""
    try:
        with get_database_session() as session:
            service = TemplateService(session)
            category = request.args.get('category')
            templates = service.get_template_list(category)
            return jsonify({
                'success': True,
                'data': templates,
                'total': len(templates)
            })
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>', methods=['GET'])
def get_template(template_id: int):
    """Get template by ID"""
    try:
        with get_database_session() as session:
            service = TemplateService(session)
            template = service.get_template_detail(template_id)

            if template:
                return jsonify({
                    'success': True,
                    'data': template
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Template not found'
                }), 404
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/search', methods=['GET'])
def search_templates():
    """Search templates"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400

        with get_database_session() as session:
            service = TemplateService(session)
            results = service.search_templates(query, category)

            return jsonify({
                'success': True,
                'data': results,
                'query': query,
                'total': len(results)
            })
    except Exception as e:
        logger.error(f"Error searching templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('', methods=['POST'])
def create_template():
    """Create new template"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Get user ID (you'll need to implement authentication)
        user_id = request.headers.get('X-User-ID', 'system')

        with get_database_session() as session:
            service = TemplateService(session)
            template, errors = service.create_template(data, user_id)

            if template:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': template.id,
                        'uuid': template.uuid,
                        'name': template.name,
                        'created_at': template.created_at.isoformat() if template.created_at else None
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>', methods=['PUT'])
def update_template(template_id: int):
    """Update existing template"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Get user ID
        user_id = request.headers.get('X-User-ID', 'system')

        with get_database_session() as session:
            service = TemplateService(session)
            template, errors = service.update_template(template_id, data, user_id)

            if template:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': template.id,
                        'uuid': template.uuid,
                        'name': template.name,
                        'updated_at': template.updated_at.isoformat() if template.updated_at else None,
                        'version': template.version
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400 if errors else 404
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>', methods=['DELETE'])
def delete_template(template_id: int):
    """Delete template (soft delete)"""
    try:
        # Get user ID
        user_id = request.headers.get('X-User-ID', 'system')

        with get_database_session() as session:
            service = TemplateService(session)
            success, errors = service.delete_template(template_id, user_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Template deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 404 if errors else 500
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>/clone', methods=['POST'])
def clone_template(template_id: int):
    """Clone existing template"""
    try:
        data = request.get_json()
        new_name = data.get('name')

        if not new_name:
            return jsonify({
                'success': False,
                'error': 'New template name is required'
            }), 400

        # Get user ID
        user_id = request.headers.get('X-User-ID', 'system')

        with get_database_session() as session:
            service = TemplateService(session)
            cloned_template, errors = service.clone_template(template_id, new_name, user_id)

            if cloned_template:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': cloned_template.id,
                        'uuid': cloned_template.uuid,
                        'name': cloned_template.name,
                        'created_at': cloned_template.created_at.isoformat() if cloned_template.created_at else None
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400 if errors else 404
    except Exception as e:
        logger.error(f"Error cloning template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>/run', methods=['POST'])
def run_template(template_id: int):
    """Execute template and generate report"""
    try:
        data = request.get_json()
        parameters = data.get('parameters', {})
        estates = data.get('estates', [])
        output_format = data.get('output_format', 'pdf')

        # Get user ID
        user_id = request.headers.get('X-User-ID', 'system')

        # Get template
        with get_database_session() as session:
            repo = ReportTemplateRepository(session)
            template = repo.get_template_by_id(template_id)

            if not template:
                return jsonify({
                    'success': False,
                    'error': 'Template not found'
                }), 404

        # Prepare execution parameters
        execution_params = {
            'template_uuid': template.uuid,
            'estates': estates,
            'start_date': parameters.get('START_DATE'),
            'end_date': parameters.get('END_DATE'),
            'output_format': output_format,
            'report_title': parameters.get('REPORT_TITLE', template.name),
            'user_id': user_id
        }

        # Get multi-estate manager
        multi_estate_manager = get_multi_estate_manager()
        if not multi_estate_manager:
            return jsonify({
                'success': False,
                'error': 'Multi-estate manager not initialized'
            }), 500

        # Initialize Jasper service
        jasper_service = JasperReportService(multi_estate_manager)

        # Generate report
        success, message, output_path = jasper_service.generate_ffb_report(
            template.uuid, execution_params, user_id
        )

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'output_path': output_path,
                'download_url': f'/api/reports/download?file={os.path.basename(output_path)}'
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500

    except Exception as e:
        logger.error(f"Error running template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>/validate', methods=['POST'])
def validate_template(template_id: int):
    """Validate template configuration"""
    try:
        data = request.get_json()
        sample_parameters = data.get('parameters', {})

        with get_database_session() as session:
            service = TemplateService(session)
            is_valid, errors, validation_result = service.validate_template_with_sample_data(
                template_id, sample_parameters
            )

            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'errors': errors,
                'validation_result': validation_result
            })

    except Exception as e:
        logger.error(f"Error validating template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/validate-sql', methods=['POST'])
def validate_sql():
    """Validate SQL query"""
    try:
        data = request.get_json()
        sql_query = data.get('sql_query', '').strip()

        if not sql_query:
            return jsonify({
                'success': False,
                'error': 'SQL query is required',
                'valid': False
            }), 400

        # Simple SQL validation
        errors = []
        sql_upper = sql_query.upper()

        # Check for dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
            'TRUNCATE', 'EXECUTE', 'GRANT', 'REVOKE'
        ]

        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                errors.append(f"Dangerous SQL keyword detected: {keyword}")

        # Check if it's a SELECT statement
        if not sql_upper.strip().startswith('SELECT'):
            errors.append("Only SELECT statements are allowed")

        # Check parameter placeholders
        if '$P{' in sql_query:
            import re
            invalid_params = re.findall(r'\$P{[^}]*[^a-zA-Z0-9_}][^}]*}', sql_query)
            if invalid_params:
                errors.append(f"Invalid parameter placeholders: {invalid_params}")

        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors
        })

    except Exception as e:
        logger.error(f"Error validating SQL: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'valid': False
        }), 500

@templates_bp.route('/preview-sql', methods=['POST'])
def preview_sql():
    """Preview SQL with sample data"""
    try:
        data = request.get_json()
        sql_query = data.get('sql_query', '').strip()
        parameters = data.get('parameters', [])

        if not sql_query:
            return jsonify({
                'success': False,
                'error': 'SQL query is required'
            }), 400

        # Generate sample data (mock implementation)
        # In a real implementation, you would execute the query with sample parameters
        sample_data = [
            {
                'TRANSNO': 'T001',
                'DIVNAME': 'PGE 1A',
                'EMPNAME': 'John Doe',
                'RECORDTAG': 'PM',
                'TRANSDATE': '2025-09-01',
                'AFD': 'A1',
                'BLOCK': 'B1',
                'TREECOUNT': 100,
                'BUNCHCOUNT': 50,
                'WEIGHT': 1000.5,
                'TBS': 150
            },
            {
                'TRANSNO': 'T001',
                'DIVNAME': 'PGE 1A',
                'EMPNAME': 'Jane Smith',
                'RECORDTAG': 'P1',
                'TRANSDATE': '2025-09-01',
                'AFD': 'A1',
                'BLOCK': 'B1',
                'TREECOUNT': 100,
                'BUNCHCOUNT': 50,
                'WEIGHT': 1000.5,
                'TBS': 150
            },
            {
                'TRANSNO': 'T002',
                'DIVNAME': 'PGE 1B',
                'EMPNAME': 'Bob Wilson',
                'RECORDTAG': 'PM',
                'TRANSDATE': '2025-09-02',
                'AFD': 'A2',
                'BLOCK': 'B2',
                'TREECOUNT': 150,
                'BUNCHCOUNT': 75,
                'WEIGHT': 1500.0,
                'TBS': 225
            }
        ]

        # Generate SQL by replacing parameters
        generated_sql = sql_query
        for param in parameters:
            param_name = param.get('name')
            param_value = param.get('default_value', '')
            placeholder = f"$P{{{param_name}}}"
            generated_sql = generated_sql.replace(placeholder, f"'{param_value}'")

        return jsonify({
            'success': True,
            'generated_sql': generated_sql,
            'data': sample_data
        })

    except Exception as e:
        logger.error(f"Error previewing SQL: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>/versions', methods=['GET'])
def get_template_versions(template_id: int):
    """Get template version history"""
    try:
        with get_database_session() as session:
            repo = ReportTemplateRepository(session)
            versions = repo.get_template_versions(template_id)

            version_list = []
            for version in versions:
                version_list.append({
                    'id': version.id,
                    'version_number': version.version_number,
                    'changelog': version.changelog,
                    'created_by': version.created_by,
                    'created_at': version.created_at.isoformat() if version.created_at else None,
                    'is_active': version.is_active
                })

            return jsonify({
                'success': True,
                'data': version_list,
                'total': len(version_list)
            })

    except Exception as e:
        logger.error(f"Error getting template versions for {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>/versions/<int:version_id>/restore', methods=['POST'])
def restore_template_version(template_id: int, version_id: int):
    """Restore template to specific version"""
    try:
        # Get user ID
        user_id = request.headers.get('X-User-ID', 'system')

        with get_database_session() as session:
            repo = ReportTemplateRepository(session)

            # Get version to restore
            versions = repo.get_template_versions(template_id)
            target_version = None

            for version in versions:
                if version.id == version_id:
                    target_version = version
                    break

            if not target_version:
                return jsonify({
                    'success': False,
                    'error': 'Version not found'
                }), 404

            # Deactivate current versions
            repo.session.query(TemplateVersion).filter(
                TemplateVersion.template_id == template_id
            ).update({TemplateVersion.is_active: False})

            # Create new version from old version
            new_version = TemplateVersion(
                template_id=template_id,
                version_number=target_version.version_number + 1,
                template_content=target_version.template_content,
                changelog=f"Restored from version {target_version.version_number}",
                created_by=user_id,
                is_active=True
            )
            repo.session.add(new_version)
            repo.session.commit()

            return jsonify({
                'success': True,
                'message': f'Template restored to version {target_version.version_number}',
                'new_version': new_version.version_number
            })

    except Exception as e:
        logger.error(f"Error restoring template version: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/categories', methods=['GET'])
def get_template_categories():
    """Get all template categories"""
    try:
        with get_database_session() as session:
            service = TemplateService(session)
            categories = service.get_template_categories()

            return jsonify({
                'success': True,
                'data': categories
            })

    except Exception as e:
        logger.error(f"Error getting template categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@templates_bp.route('/<int:template_id>/download', methods=['GET'])
def download_template(template_id: int):
    """Download template file"""
    try:
        with get_database_session() as session:
            repo = ReportTemplateRepository(session)
            template = repo.get_template_by_id(template_id)

            if not template:
                return jsonify({
                    'success': False,
                    'error': 'Template not found'
                }), 404

            if not template.template_content:
                return jsonify({
                    'success': False,
                    'error': 'Template content not found'
                }), 404

            # Create temporary file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{template.name}_{timestamp}.jrxml"

            with tempfile.NamedTemporaryFile(mode='wb', suffix='.jrxml', delete=False) as temp_file:
                temp_file.write(template.template_content)
                temp_path = temp_file.name

            try:
                return send_file(
                    temp_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/xml'
                )
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error downloading template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500