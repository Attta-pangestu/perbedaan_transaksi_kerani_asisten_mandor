"""
Template Service - Business Logic untuk Template Management
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.models import ReportTemplate, TemplateParameter, TemplateVersion, TemplateExecution
from ..database.repositories import ReportTemplateRepository, TemplateParameterRepository, FFBDataRepository
from ..database.connection import FirebirdConnectionManager

logger = logging.getLogger(__name__)

class TemplateService:
    """
    Service untuk template management operations
    """

    def __init__(self, session: Session):
        self.session = session
        self.template_repo = ReportTemplateRepository(session)
        self.parameter_repo = TemplateParameterRepository(session)

    def create_template(self, template_data: Dict[str, Any], user_id: str) -> Tuple[Optional[ReportTemplate], List[str]]:
        """
        Create new template dengan validation

        Args:
            template_data: Template data
            user_id: User ID yang membuat

        Returns:
            Tuple of (created_template, error_messages)
        """
        errors = []

        # Validation
        validation_errors = self._validate_template_data(template_data)
        errors.extend(validation_errors)

        if errors:
            return None, errors

        # Prepare template data
        template_data['created_by'] = user_id
        template_data['updated_by'] = user_id

        # Parse parameter schema jika ada
        if 'parameter_schema' in template_data and isinstance(template_data['parameter_schema'], str):
            try:
                template_data['parameter_schema'] = json.loads(template_data['parameter_schema'])
            except json.JSONDecodeError:
                errors.append("Invalid parameter schema JSON format")

        try:
            template = self.template_repo.create_template(template_data)

            # Create parameters jika ada
            if 'parameters' in template_data:
                for param_data in template_data['parameters']:
                    param_data['template_id'] = template.id
                    param_data['created_by'] = user_id
                    self.parameter_repo.create_parameter(param_data)

            logger.info(f"Template created: {template.name} by {user_id}")
            return template, []

        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            errors.append(f"Database error: {str(e)}")
            return None, errors

    def update_template(self, template_id: int, update_data: Dict[str, Any], user_id: str) -> Tuple[Optional[ReportTemplate], List[str]]:
        """
        Update existing template

        Args:
            template_id: Template ID
            update_data: Update data
            user_id: User ID yang update

        Returns:
            Tuple of (updated_template, error_messages)
        """
        errors = []

        # Validate template exists
        template = self.template_repo.get_template_by_id(template_id)
        if not template:
            errors.append("Template not found")
            return None, errors

        # Validate update data
        if 'name' in update_data:
            if not update_data['name'] or len(update_data['name'].strip()) == 0:
                errors.append("Template name cannot be empty")

        if 'sql_query' in update_data:
            sql_errors = self._validate_sql_query(update_data['sql_query'])
            errors.extend(sql_errors)

        if errors:
            return None, errors

        # Prepare update data
        update_data['updated_by'] = user_id
        update_data['updated_at'] = datetime.now()

        # Parse parameter schema jika ada
        if 'parameter_schema' in update_data and isinstance(update_data['parameter_schema'], str):
            try:
                update_data['parameter_schema'] = json.loads(update_data['parameter_schema'])
            except json.JSONDecodeError:
                errors.append("Invalid parameter schema JSON format")

        try:
            updated_template = self.template_repo.update_template(
                template_id, update_data, create_version=True
            )
            logger.info(f"Template updated: {updated_template.name} by {user_id}")
            return updated_template, []

        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            errors.append(f"Database error: {str(e)}")
            return None, errors

    def delete_template(self, template_id: int, user_id: str) -> Tuple[bool, List[str]]:
        """
        Delete template (soft delete)

        Args:
            template_id: Template ID
            user_id: User ID yang delete

        Returns:
            Tuple of (success, error_messages)
        """
        errors = []

        template = self.template_repo.get_template_by_id(template_id)
        if not template:
            errors.append("Template not found")
            return False, errors

        try:
            success = self.template_repo.delete_template(template_id)
            if success:
                logger.info(f"Template deleted: {template.name} by {user_id}")
            return success, []

        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            errors.append(f"Database error: {str(e)}")
            return False, errors

    def get_template_list(self, category: str = None, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get list templates dengan additional info

        Args:
            category: Filter by category
            include_inactive: Include inactive templates

        Returns:
            List of template dictionaries
        """
        if category:
            templates = self.template_repo.get_templates_by_category(category)
        else:
            templates = self.template_repo.get_all_templates(include_inactive)

        result = []
        for template in templates:
            # Get execution statistics
            executions = self.template_repo.get_executions_by_template(template.id, limit=5)

            template_dict = {
                'id': template.id,
                'uuid': template.uuid,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'template_type': template.template_type,
                'is_active': template.is_active,
                'is_public': template.is_public,
                'created_by': template.created_by,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None,
                'version': template.version,
                'execution_count': len(executions),
                'last_execution': executions[0].executed_at.isoformat() if executions else None,
                'parameters': self.get_template_parameters(template.id)
            }
            result.append(template_dict)

        return result

    def get_template_detail(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed template information

        Args:
            template_id: Template ID

        Returns:
            Template dictionary or None
        """
        template = self.template_repo.get_template_by_id(template_id)
        if not template:
            return None

        # Get active version
        active_version = self.template_repo.get_active_version(template_id)
        versions = self.template_repo.get_template_versions(template_id)

        # Get recent executions
        recent_executions = self.template_repo.get_executions_by_template(template_id, limit=10)

        template_dict = {
            'id': template.id,
            'uuid': template.uuid,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'template_type': template.template_type,
            'sql_query': template.sql_query,
            'parameter_schema': template.parameter_schema,
            'is_active': template.is_active,
            'is_public': template.is_public,
            'created_by': template.created_by,
            'created_at': template.created_at.isoformat() if template.created_at else None,
            'updated_by': template.updated_by,
            'updated_at': template.updated_at.isoformat() if template.updated_at else None,
            'version': template.version,
            'parameters': self.get_template_parameters(template_id),
            'active_version': {
                'id': active_version.id,
                'version_number': active_version.version_number,
                'changelog': active_version.changelog,
                'created_at': active_version.created_at.isoformat() if active_version.created_at else None
            } if active_version else None,
            'versions': [
                {
                    'id': v.id,
                    'version_number': v.version_number,
                    'changelog': v.changelog,
                    'created_at': v.created_at.isoformat() if v.created_at else None,
                    'is_active': v.is_active
                } for v in versions
            ],
            'recent_executions': [
                {
                    'id': e.id,
                    'status': e.status,
                    'executed_at': e.executed_at.isoformat() if e.executed_at else None,
                    'execution_time': e.execution_time,
                    'record_count': e.record_count,
                    'executed_by': e.executed_by
                } for e in recent_executions
            ]
        }

        return template_dict

    def get_template_parameters(self, template_id: int) -> List[Dict[str, Any]]:
        """Get parameters for a template"""
        parameters = self.parameter_repo.get_parameters_by_template(template_id)
        return [
            {
                'id': p.id,
                'name': p.name,
                'parameter_type': p.parameter_type,
                'display_name': p.display_name,
                'description': p.description,
                'default_value': p.default_value,
                'is_required': p.is_required,
                'validation_rule': p.validation_rule,
                'ui_component': p.ui_component,
                'options': p.options,
                'order_index': p.order_index
            } for p in parameters
        ]

    def clone_template(self, template_id: int, new_name: str, user_id: str) -> Tuple[Optional[ReportTemplate], List[str]]:
        """
        Clone existing template

        Args:
            template_id: Source template ID
            new_name: New template name
            user_id: User ID yang clone

        Returns:
            Tuple of (cloned_template, error_messages)
        """
        errors = []

        # Get source template
        source_template = self.template_repo.get_template_by_id(template_id)
        if not source_template:
            errors.append("Source template not found")
            return None, errors

        # Prepare clone data
        clone_data = {
            'name': new_name,
            'description': f"Cloned from: {source_template.description}",
            'category': source_template.category,
            'template_type': source_template.template_type,
            'template_content': source_template.template_content,
            'sql_query': source_template.sql_query,
            'parameter_schema': source_template.parameter_schema,
            'is_public': False,  # Cloned templates are private by default
            'created_by': user_id,
            'updated_by': user_id
        }

        # Create cloned template
        cloned_template, clone_errors = self.create_template(clone_data, user_id)
        if clone_errors:
            errors.extend(clone_errors)

        return cloned_template, errors

    def validate_template_with_sample_data(self, template_id: int, sample_parameters: Dict[str, Any] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate template dengan sample data

        Args:
            template_id: Template ID
            sample_parameters: Sample parameters for validation

        Returns:
            Tuple of (is_valid, error_messages, validation_result)
        """
        errors = []
        template = self.template_repo.get_template_by_id(template_id)

        if not template:
            errors.append("Template not found")
            return False, errors, {}

        # Validate SQL query syntax
        if template.sql_query:
            sql_errors = self._validate_sql_query(template.sql_query)
            errors.extend(sql_errors)

        # Validate parameter schema
        if template.parameter_schema:
            try:
                schema = json.loads(template.parameter_schema) if isinstance(template.parameter_schema, str) else template.parameter_schema
                param_errors = self._validate_parameter_schema(schema)
                errors.extend(param_errors)
            except Exception as e:
                errors.append(f"Invalid parameter schema: {str(e)}")

        # Prepare validation result
        validation_result = {
            'template_id': template_id,
            'template_name': template.name,
            'validation_time': datetime.now().isoformat(),
            'sql_query_valid': len([e for e in errors if 'SQL' in e]) == 0,
            'parameter_schema_valid': len([e for e in errors if 'parameter' in e.lower()]) == 0,
            'parameter_count': len(self.get_template_parameters(template_id))
        }

        return len(errors) == 0, errors, validation_result

    def _validate_template_data(self, template_data: Dict[str, Any]) -> List[str]:
        """Validate template data"""
        errors = []

        # Required fields
        if not template_data.get('name') or len(template_data['name'].strip()) == 0:
            errors.append("Template name is required")

        if template_data.get('name') and len(template_data['name']) > 255:
            errors.append("Template name too long (max 255 characters)")

        # Validate template type
        valid_types = ['JASPER', 'HTML', 'EXCEL', 'CSV']
        if template_data.get('template_type') and template_data['template_type'] not in valid_types:
            errors.append(f"Invalid template type. Must be one of: {', '.join(valid_types)}")

        # Validate SQL query
        if template_data.get('sql_query'):
            sql_errors = self._validate_sql_query(template_data['sql_query'])
            errors.extend(sql_errors)

        return errors

    def _validate_sql_query(self, query: str) -> List[str]:
        """Validate SQL query untuk security"""
        errors = []

        if not query or not query.strip():
            return ["SQL query cannot be empty"]

        query_upper = query.upper()

        # Check untuk dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
            'TRUNCATE', 'EXECUTE', 'GRANT', 'REVOKE'
        ]

        for keyword in dangerous_keywords:
            if re.search(r'\b' + keyword + r'\b', query_upper):
                errors.append(f" Dangerous SQL keyword detected: {keyword}")

        # Check untuk proper SELECT statement
        if not query_upper.strip().startswith('SELECT'):
            errors.append("Only SELECT statements are allowed")

        # Check untuk parameter placeholder format
        if '$P{' in query:
            # Validate parameter placeholder format
            invalid_params = re.findall(r'\$P{[^}]*[^a-zA-Z0-9_}][^}]*}', query)
            if invalid_params:
                errors.append(f"Invalid parameter placeholders: {invalid_params}")

        return errors

    def _validate_parameter_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Validate parameter schema"""
        errors = []

        if not isinstance(schema, dict):
            errors.append("Parameter schema must be a dictionary")
            return errors

        # Check required fields
        required_fields = ['name', 'type']
        for param in schema.get('parameters', []):
            for field in required_fields:
                if field not in param:
                    errors.append(f"Parameter missing required field: {field}")

            # Validate parameter type
            valid_types = ['STRING', 'NUMBER', 'DATE', 'BOOLEAN', 'LIST', 'ESTATE', 'DATE_RANGE']
            if param.get('type') and param['type'] not in valid_types:
                errors.append(f"Invalid parameter type: {param['type']}")

        return errors

    def get_template_categories(self) -> List[str]:
        """Get all unique template categories"""
        templates = self.template_repo.get_all_templates()
        categories = set(template.category for template in templates if template.category)
        return sorted(list(categories))

    def search_templates(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """
        Search templates by name, description, or SQL query

        Args:
            query: Search query
            category: Filter by category

        Returns:
            List of matching templates
        """
        templates = self.template_repo.get_all_templates()
        results = []

        search_query = query.lower()

        for template in templates:
            # Category filter
            if category and template.category != category:
                continue

            # Search in name, description, and SQL query
            searchable_text = ' '.join([
                template.name or '',
                template.description or '',
                template.sql_query or ''
            ]).lower()

            if search_query in searchable_text:
                results.append({
                    'id': template.id,
                    'uuid': template.uuid,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'template_type': template.template_type,
                    'created_at': template.created_at.isoformat() if template.created_at else None,
                    'updated_at': template.updated_at.isoformat() if template.updated_at else None
                })

        return results