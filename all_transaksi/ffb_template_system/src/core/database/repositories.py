"""
Database Repositories untuk FFB Template System
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date
import json

from .models import ReportTemplate, TemplateVersion, TemplateExecution, TemplateParameter, User, SystemConfig, AuditLog
from .connection import FirebirdConnectionManager

class ReportTemplateRepository:
    """
    Repository untuk ReportTemplate operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create_template(self, template_data: Dict[str, Any]) -> ReportTemplate:
        """
        Create new report template

        Args:
            template_data: Template data dictionary

        Returns:
            Created ReportTemplate instance
        """
        template = ReportTemplate(**template_data)
        self.session.add(template)
        self.session.flush()  # Get ID without committing

        # Create initial version
        initial_version = TemplateVersion(
            template_id=template.id,
            version_number=1,
            template_content=template.template_content,
            changelog="Initial version",
            created_by=template.created_by,
            is_active=True
        )
        self.session.add(initial_version)

        self.session.commit()
        self.session.refresh(template)
        return template

    def get_template_by_id(self, template_id: int) -> Optional[ReportTemplate]:
        """Get template by ID"""
        return self.session.query(ReportTemplate).filter(
            ReportTemplate.id == template_id,
            ReportTemplate.is_active == True
        ).first()

    def get_template_by_uuid(self, uuid: str) -> Optional[ReportTemplate]:
        """Get template by UUID"""
        return self.session.query(ReportTemplate).filter(
            ReportTemplate.uuid == uuid,
            ReportTemplate.is_active == True
        ).first()

    def get_all_templates(self, include_inactive: bool = False) -> List[ReportTemplate]:
        """Get all templates"""
        query = self.session.query(ReportTemplate)
        if not include_inactive:
            query = query.filter(ReportTemplate.is_active == True)
        return query.order_by(desc(ReportTemplate.updated_at)).all()

    def get_templates_by_category(self, category: str) -> List[ReportTemplate]:
        """Get templates by category"""
        return self.session.query(ReportTemplate).filter(
            ReportTemplate.category == category,
            ReportTemplate.is_active == True
        ).order_by(ReportTemplate.name).all()

    def update_template(self, template_id: int, update_data: Dict[str, Any],
                       create_version: bool = True) -> Optional[ReportTemplate]:
        """
        Update existing template

        Args:
            template_id: Template ID
            update_data: Update data
            create_version: Whether to create new version

        Returns:
            Updated template or None
        """
        template = self.get_template_by_id(template_id)
        if not template:
            return None

        # Store old values for audit
        old_values = {
            'name': template.name,
            'description': template.description,
            'sql_query': template.sql_query,
            'template_type': template.template_type
        }

        # Update template fields
        for key, value in update_data.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now()

        # Create new version if content changed
        if create_version and 'template_content' in update_data:
            # Deactivate old versions
            self.session.query(TemplateVersion).filter(
                TemplateVersion.template_id == template_id
            ).update({TemplateVersion.is_active: False})

            # Get next version number
            max_version = self.session.query(func.max(TemplateVersion.version_number)).filter(
                TemplateVersion.template_id == template_id
            ).scalar() or 0

            # Create new version
            new_version = TemplateVersion(
                template_id=template_id,
                version_number=max_version + 1,
                template_content=update_data.get('template_content'),
                changelog=update_data.get('changelog', 'Updated template'),
                created_by=update_data.get('updated_by'),
                is_active=True
            )
            self.session.add(new_version)

        self.session.commit()
        self.session.refresh(template)
        return template

    def delete_template(self, template_id: int) -> bool:
        """Soft delete template"""
        template = self.get_template_by_id(template_id)
        if template:
            template.is_active = False
            template.updated_at = datetime.now()
            self.session.commit()
            return True
        return False

    def get_template_versions(self, template_id: int) -> List[TemplateVersion]:
        """Get all versions of a template"""
        return self.session.query(TemplateVersion).filter(
            TemplateVersion.template_id == template_id
        ).order_by(desc(TemplateVersion.version_number)).all()

    def get_active_version(self, template_id: int) -> Optional[TemplateVersion]:
        """Get active version of a template"""
        return self.session.query(TemplateVersion).filter(
            TemplateVersion.template_id == template_id,
            TemplateVersion.is_active == True
        ).first()


class TemplateExecutionRepository:
    """
    Repository untuk TemplateExecution operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create_execution(self, execution_data: Dict[str, Any]) -> TemplateExecution:
        """Create new template execution record"""
        execution = TemplateExecution(**execution_data)
        self.session.add(execution)
        self.session.commit()
        self.session.refresh(execution)
        return execution

    def update_execution_status(self, execution_id: int, status: str,
                               execution_time: float = None, record_count: int = None,
                               output_path: str = None, error_message: str = None) -> bool:
        """Update execution status"""
        execution = self.session.query(TemplateExecution).filter(
            TemplateExecution.id == execution_id
        ).first()

        if execution:
            execution.status = status
            execution.completed_at = datetime.now()

            if execution_time is not None:
                execution.execution_time = execution_time
            if record_count is not None:
                execution.record_count = record_count
            if output_path:
                execution.output_file_path = output_path
            if error_message:
                execution.error_message = error_message

            self.session.commit()
            return True
        return False

    def get_execution_by_id(self, execution_id: int) -> Optional[TemplateExecution]:
        """Get execution by ID"""
        return self.session.query(TemplateExecution).filter(
            TemplateExecution.id == execution_id
        ).first()

    def get_executions_by_template(self, template_id: int, limit: int = 50) -> List[TemplateExecution]:
        """Get executions for a template"""
        return self.session.query(TemplateExecution).filter(
            TemplateExecution.template_id == template_id
        ).order_by(desc(TemplateExecution.executed_at)).limit(limit).all()

    def get_user_executions(self, user_id: int, limit: int = 50) -> List[TemplateExecution]:
        """Get executions by user"""
        return self.session.query(TemplateExecution).filter(
            TemplateExecution.executed_by == str(user_id)
        ).order_by(desc(TemplateExecution.executed_at)).limit(limit).all()


class TemplateParameterRepository:
    """
    Repository untuk TemplateParameter operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create_parameter(self, parameter_data: Dict[str, Any]) -> TemplateParameter:
        """Create new template parameter"""
        parameter = TemplateParameter(**parameter_data)
        self.session.add(parameter)
        self.session.commit()
        self.session.refresh(parameter)
        return parameter

    def get_parameters_by_template(self, template_id: int) -> List[TemplateParameter]:
        """Get parameters for a template"""
        return self.session.query(TemplateParameter).filter(
            TemplateParameter.template_id == template_id
        ).order_by(TemplateParameter.order_index).all()

    def update_parameter(self, parameter_id: int, update_data: Dict[str, Any]) -> Optional[TemplateParameter]:
        """Update parameter"""
        parameter = self.session.query(TemplateParameter).filter(
            TemplateParameter.id == parameter_id
        ).first()

        if parameter:
            for key, value in update_data.items():
                if hasattr(parameter, key):
                    setattr(parameter, key, value)
            self.session.commit()
            self.session.refresh(parameter)
            return parameter
        return None

    def delete_parameter(self, parameter_id: int) -> bool:
        """Delete parameter"""
        parameter = self.session.query(TemplateParameter).filter(
            TemplateParameter.id == parameter_id
        ).first()

        if parameter:
            self.session.delete(parameter)
            self.session.commit()
            return True
        return False


class UserRepository:
    """
    Repository untuk User operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create new user"""
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.query(User).filter(User.username == username).first()

    def get_all_users(self) -> List[User]:
        """Get all active users"""
        return self.session.query(User).filter(User.is_active == True).all()

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user"""
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(user)
            return user
        return None


class FFBDataRepository:
    """
    Repository untuk FFB transaction data operations
    """

    def __init__(self, connection_manager: FirebirdConnectionManager):
        self.connection_manager = connection_manager

    def get_monthly_tables(self, start_date: date, end_date: date) -> List[str]:
        """Get available monthly tables for date range"""
        tables = []
        current_month = start_date.month
        current_year = start_date.year

        while (current_year < end_date.year) or \
              (current_year == end_date.year and current_month <= end_date.month):
            table_name = f"FFBSCANNERDATA{current_month:02d}"
            tables.append(table_name)

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        return tables

    def check_table_exists(self, table_name: str) -> bool:
        """Check if monthly table exists"""
        try:
            with self.connection_manager.get_session() as session:
                result = session.execute(text(
                    "SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = :table_name"
                ), {"table_name": table_name})
                return result.fetchone()[0] > 0
        except Exception:
            return False

    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Execute dynamic query dengan parameter substitution

        Args:
            query: SQL query dengan placeholders
            parameters: Parameter values

        Returns:
            List of dictionaries dengan query results
        """
        try:
            with self.connection_manager.get_session() as session:
                # Use text() untuk raw SQL
                sql_text = text(query)

                if parameters:
                    result = session.execute(sql_text, parameters)
                else:
                    result = session.execute(sql_text)

                # Convert ke list of dictionaries
                columns = result.keys()
                rows = []
                for row in result:
                    row_dict = dict(zip(columns, row))
                    rows.append(row_dict)

                return rows

        except Exception as e:
            raise Exception(f"Query execution failed: {e}")

    def get_ffb_transactions(self, estates: List[str], start_date: date, end_date: date,
                           record_types: List[str] = None) -> List[Dict]:
        """
        Get FFB transactions untuk multiple estates dan date range

        Args:
            estates: List estate names
            start_date: Start date
            end_date: End date
            record_types: List record types (PM, P1, P5)

        Returns:
            List of transaction dictionaries
        """
        # Get available monthly tables
        monthly_tables = self.get_monthly_tables(start_date, end_date)

        all_transactions = []

        for table_name in monthly_tables:
            if not self.check_table_exists(table_name):
                continue

            # Build query untuk each monthly table
            query = f"""
                SELECT
                    a.TRANSNO, a.SCANUSERID, a.RECORDTAG, a.TRANSDATE,
                    a.FIELDID, a.AFD, a.BLOCK, a.TREECOUNT, a.BUNCHCOUNT,
                    a.LOOSEFRUIT, a.WEIGHT, a.TBS, a.HARVESTER, a.TAKENBY,
                    b.DIVID, c.DIVNAME, d.EMPNAME
                FROM {table_name} a
                JOIN OCFIELD b ON a.FIELDID = b.ID
                LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
                LEFT JOIN EMP d ON a.SCANUSERID = d.EMPID
                WHERE a.TRANSDATE BETWEEN :start_date AND :end_date
            """

            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }

            # Add estate filter
            if estates:
                estate_placeholders = ', '.join([f':estate_{i}' for i in range(len(estates))])
                query += f" AND c.DIVNAME IN ({estate_placeholders})"
                for i, estate in enumerate(estates):
                    params[f'estate_{i}'] = estate

            # Add record type filter
            if record_types:
                type_placeholders = ', '.join([f':type_{i}' for i in range(len(record_types))])
                query += f" AND a.RECORDTAG IN ({type_placeholders})"
                for i, record_type in enumerate(record_types):
                    params[f'type_{i}'] = record_type

            query += " ORDER BY a.TRANSDATE, a.TRANSNO"

            try:
                transactions = self.execute_query(query, params)
                all_transactions.extend(transactions)
            except Exception as e:
                # Log error but continue with other tables
                print(f"Error querying {table_name}: {e}")

        return all_transactions