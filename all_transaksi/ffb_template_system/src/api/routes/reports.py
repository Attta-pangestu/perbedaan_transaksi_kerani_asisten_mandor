"""
Reports API Routes
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime

from ...core.database.repositories import TemplateExecutionRepository, ReportTemplateRepository
from ...core.database.connection import get_database_session
from ...app import get_multi_estate_manager

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('', methods=['GET'])
def get_reports():
    """Get recent reports"""
    try:
        limit = request.args.get('limit', 50, type=int)
        template_id = request.args.get('template_id', type=int)
        user_id = request.args.get('user_id')
        status = request.args.get('status')

        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)

            if template_id:
                reports = repo.get_executions_by_template(template_id, limit)
            elif user_id:
                reports = repo.get_user_executions(user_id, limit)
            else:
                # Get all recent executions
                # This would need to be implemented in the repository
                reports = session.query(TemplateExecution)\
                    .filter(TemplateExecution.status == 'SUCCESS')\
                    .order_by(TemplateExecution.executed_at.desc())\
                    .limit(limit).all()

            report_list = []
            for report in reports:
                report_list.append({
                    'id': report.id,
                    'uuid': report.uuid,
                    'template_id': report.template_id,
                    'template_name': get_template_name(session, report.template_id),
                    'status': report.status,
                    'execution_time': report.execution_time,
                    'record_count': report.record_count,
                    'output_file_path': report.output_file_path,
                    'output_format': report.output_format,
                    'parameters': report.parameters,
                    'estates': report.estates,
                    'date_range': report.date_range,
                    'executed_by': report.executed_by,
                    'executed_at': report.executed_at.isoformat() if report.executed_at else None,
                    'completed_at': report.completed_at.isoformat() if report.completed_at else None,
                    'error_message': report.error_message
                })

            return jsonify({
                'success': True,
                'data': report_list,
                'total': len(report_list)
            })

    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_template_name(session: Session, template_id: int) -> str:
    """Helper function to get template name"""
    try:
        template_repo = ReportTemplateRepository(session)
        template = template_repo.get_template_by_id(template_id)
        return template.name if template else 'Unknown'
    except:
        return 'Unknown'

@reports_bp.route('/<int:report_id>', methods=['GET'])
def get_report(report_id: int):
    """Get specific report details"""
    try:
        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)
            report = repo.get_execution_by_id(report_id)

            if not report:
                return jsonify({
                    'success': False,
                    'error': 'Report not found'
                }), 404

            # Get template information
            template_name = get_template_name(session, report.template_id)

            report_data = {
                'id': report.id,
                'uuid': report.uuid,
                'template_id': report.template_id,
                'template_name': template_name,
                'status': report.status,
                'execution_time': report.execution_time,
                'record_count': report.record_count,
                'output_file_path': report.output_file_path,
                'output_format': report.output_format,
                'parameters': report.parameters,
                'estates': report.estates,
                'date_range': report.date_range,
                'executed_by': report.executed_by,
                'executed_at': report.executed_at.isoformat() if report.executed_at else None,
                'completed_at': report.completed_at.isoformat() if report.completed_at else None,
                'error_message': report.error_message
            }

            return jsonify({
                'success': True,
                'data': report_data
            })

    except Exception as e:
        logger.error(f"Error getting report {report_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/<int:report_id>/download', methods=['GET'])
def download_report(report_id: int):
    """Download report file"""
    try:
        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)
            report = repo.get_execution_by_id(report_id)

            if not report:
                return jsonify({
                    'success': False,
                    'error': 'Report not found'
                }), 404

            if not report.output_file_path:
                return jsonify({
                    'success': False,
                    'error': 'Output file not available'
                }), 404

            if not os.path.exists(report.output_file_path):
                return jsonify({
                    'success': False,
                    'error': 'Output file not found'
                }), 404

            # Generate filename
            template_name = get_template_name(session, report.template_id)
            timestamp = report.executed_at.strftime('%Y%m%d_%H%M%S') if report.executed_at else 'unknown'
            filename = f"{template_name}_{timestamp}.{report.output_format}"

            return send_file(
                report.output_file_path,
                as_attachment=True,
                download_name=filename,
                mimetype=get_mimetype(report.output_format)
            )

    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/download', methods=['GET'])
def download_report_by_filename():
    """Download report by filename"""
    try:
        filename = request.args.get('file')

        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename parameter is required'
            }), 400

        # Construct file path
        reports_dir = current_app.config.get('REPORTS_FOLDER')
        file_path = os.path.join(reports_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=get_mimetype_from_filename(filename)
        )

    except Exception as e:
        logger.error(f"Error downloading report by filename: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/<int:report_id>/retry', methods=['POST'])
def retry_report(report_id: int):
    """Retry failed report generation"""
    try:
        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)
            report = repo.get_execution_by_id(report_id)

            if not report:
                return jsonify({
                    'success': False,
                    'error': 'Report not found'
                }), 404

            if report.status == 'SUCCESS':
                return jsonify({
                    'success': False,
                    'error': 'Report was successful, no need to retry'
                }), 400

            # Get template and regenerate
            template_repo = ReportTemplateRepository(session)
            template = template_repo.get_template_by_id(report.template_id)

            if not template:
                return jsonify({
                    'success': False,
                    'error': 'Template not found'
                }), 404

            # Reset execution status
            repo.update_execution_status(
                report_id,
                status='PENDING',
                error_message=None
            )

            # Trigger background task for report generation
            # In a real implementation, you would use Celery or similar
            from ...core.reports.jasper_service import JasperReportService

            multi_estate_manager = get_multi_estate_manager()
            if not multi_estate_manager:
                return jsonify({
                    'success': False,
                    'error': 'Multi-estate manager not available'
                }), 500

            jasper_service = JasperReportService(multi_estate_manager)

            # Execute report generation in background
            try:
                success, message, output_path = jasper_service.generate_ffb_report(
                    template.uuid,
                    {
                        'estates': report.estates,
                        'start_date': report.date_range.get('start_date'),
                        'end_date': report.date_range.get('end_date'),
                        'report_title': template.name,
                        'user_id': report.executed_by
                    },
                    report.executed_by
                )

                if success:
                    repo.update_execution_status(
                        report_id,
                        status='SUCCESS',
                        output_path=output_path
                    )

                    return jsonify({
                        'success': True,
                        'message': 'Report regenerated successfully'
                    })
                else:
                    repo.update_execution_status(
                        report_id,
                        status='ERROR',
                        error_message=message
                    )

                    return jsonify({
                        'success': False,
                        'error': message
                    })

            except Exception as e:
                repo.update_execution_status(
                    report_id,
                    status='ERROR',
                    error_message=str(e)
                )

                return jsonify({
                    'success': False,
                    'error': f"Report generation failed: {str(e)}"
                })

    except Exception as e:
        logger.error(f"Error retrying report {report_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/<int:report_id>/cancel', methods=['POST'])
def cancel_report(report_id: int):
    """Cancel running report"""
    try:
        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)
            report = repo.get_execution_by_id(report_id)

            if not report:
                return jsonify({
                    'success': False,
                    'error': 'Report not found'
                }), 404

            if report.status not in ['PENDING', 'RUNNING']:
                return jsonify({
                    'success': False,
                    'error': 'Report cannot be cancelled in current state'
                }), 400

            # Update status to cancelled
            success = repo.update_execution_status(
                report_id,
                status='CANCELLED',
                error_message='Report generation cancelled by user'
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Report cancelled successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to cancel report'
                }), 500

    except Exception as e:
        logger.error(f"Error cancelling report {report_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/queue', methods=['GET'])
def get_report_queue():
    """Get current report queue"""
    try:
        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)

            # Get pending and running reports
            queued_reports = session.query(TemplateExecution)\
                .filter(TemplateExecution.status.in_(['PENDING', 'RUNNING']))\
                .order_by(TemplateExecution.executed_at.asc())\
                .all()

            queue_list = []
            for report in queued_reports:
                queue_list.append({
                    'id': report.id,
                    'uuid': report.uuid,
                    'template_name': get_template_name(session, report.template_id),
                    'status': report.status,
                    'executed_at': report.executed_at.isoformat() if report.executed_at else None,
                    'executed_by': report.executed_by
                })

            return jsonify({
                'success': True,
                'data': queue_list,
                'total': len(queue_list)
            })

    except Exception as e:
        logger.error(f"Error getting report queue: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/stats', methods=['GET'])
def get_report_stats():
    """Get report generation statistics"""
    try:
        with get_database_session() as session:
            repo = TemplateExecutionRepository(session)

            # Get statistics
            stats = {
                'total_reports': 0,
                'successful_reports': 0,
                'failed_reports': 0,
                'pending_reports': 0,
                'running_reports': 0,
                'average_execution_time': 0,
                'total_records_processed': 0
            }

            # Count reports by status
            all_reports = session.query(TemplateExecution).all()

            for report in all_reports:
                stats['total_reports'] += 1

                if report.status == 'SUCCESS':
                    stats['successful_reports'] += 1
                    stats['total_records_processed'] += report.record_count or 0
                elif report.status == 'ERROR':
                    stats['failed_reports'] += 1
                elif report.status == 'PENDING':
                    stats['pending_reports'] += 1
                elif report.status == 'RUNNING':
                    stats['running_reports'] += 1

            # Calculate average execution time for successful reports
            successful_reports = [r for r in all_reports if r.status == 'SUCCESS' and r.execution_time]
            if successful_reports:
                stats['average_execution_time'] = sum(r.execution_time for r in successful_reports) / len(successful_reports)

            # Get recent activity (last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)

            recent_reports = session.query(TemplateExecution)\
                .filter(TemplateExecution.executed_at >= yesterday)\
                .order_by(TemplateExecution.executed_at.desc())\
                .all()

            recent_activity = []
            for report in recent_reports[:10]:
                recent_activity.append({
                    'id': report.id,
                    'template_name': get_template_name(session, report.template_id),
                    'status': report.status,
                    'executed_at': report.executed_at.isoformat() if report.executed_at else None,
                    'executed_by': report.executed_by
                })

            return jsonify({
                'success': True,
                'stats': stats,
                'recent_activity': recent_activity,
                'queue_size': stats['pending_reports'] + stats['running_reports']
            })

    except Exception as e:
        logger.error(f"Error getting report stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/quick-generate', methods=['POST'])
def quick_generate_report():
    """Quick report generation with default parameters"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        parameters = data.get('parameters', {})

        if not template_id:
            return jsonify({
                'success': False,
                'error': 'Template ID is required'
            }), 400

        # Get template
        with get_database_session() as session:
            repo = ReportTemplateRepository(session)
            template = repo.get_template_by_id(template_id)

            if not template:
                return jsonify({
                    'success': False,
                    'error': 'Template not found'
                }), 404

        # Create execution record
        execution_data = {
            'template_id': template_id,
            'parameters': parameters,
            'estates': parameters.get('ESTATES', ['PGE 1A']),
            'date_range': {
                'start_date': parameters.get('START_DATE', '2025-09-01'),
                'end_date': parameters.get('END_DATE', '2025-09-30')
            },
            'output_format': parameters.get('OUTPUT_FORMAT', 'pdf'),
            'executed_by': request.headers.get('X-User-ID', 'system')
        }

        with get_database_session() as session:
            execution_repo = TemplateExecutionRepository(session)
            execution = execution_repo.create_execution(execution_data)

        # Trigger background report generation
        # In real implementation, this would use Celery or similar
        # For now, we'll simulate the process
        try:
            # Update status to running
            execution_repo.update_execution_status(
                execution.id,
                status='RUNNING'
            )

            # Simulate processing time
            import time
            time.sleep(2)

            # Get multi-estate manager
            multi_estate_manager = get_multi_estate_manager()
            if not multi_estate_manager:
                execution_repo.update_execution_status(
                    execution.id,
                    status='ERROR',
                    error_message='Multi-estate manager not available'
                )
                return jsonify({
                    'success': False,
                    'error': 'Multi-estate manager not available'
                }), 500

            # Generate report
            from ...core.reports.jasper_service import JasperReportService
            jasper_service = JasperReportService(multi_estate_manager)

            success, message, output_path = jasper_service.generate_ffb_report(
                template.uuid,
                execution_data,
                execution.executed_by
            )

            if success:
                execution_repo.update_execution_status(
                    execution.id,
                    status='SUCCESS',
                    output_path=output_path,
                    record_count=100  # Mock count
                )

                return jsonify({
                    'success': True,
                    'message': 'Report generated successfully',
                    'execution_id': execution.id,
                    'output_path': output_path
                })
            else:
                execution_repo.update_execution_status(
                    execution.id,
                    status='ERROR',
                    error_message=message
                )

                return jsonify({
                    'success': False,
                    'error': message,
                    'execution_id': execution.id
                })

        except Exception as e:
            logger.error(f"Error in quick report generation: {e}")
            execution_repo.update_execution_status(
                execution.id,
                status='ERROR',
                error_message=str(e)
            )

            return jsonify({
                'success': False,
                'error': str(e),
                'execution_id': execution.id
            })

    except Exception as e:
        logger.error(f"Error in quick report generation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_mimetype(format_type: str) -> str:
    """Get MIME type for file format"""
    mimetypes = {
        'pdf': 'application/pdf',
        'html': 'text/html',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
        'xml': 'application/xml'
    }
    return mimetypes.get(format_type.lower(), 'application/octet-stream')

def get_mimetype_from_filename(filename: str) -> str:
    """Get MIME type from filename"""
    # Extract file extension
    if '.' in filename:
        ext = filename.split('.')[-1].lower()
        return get_mimetype(ext)
    return 'application/octet-stream'