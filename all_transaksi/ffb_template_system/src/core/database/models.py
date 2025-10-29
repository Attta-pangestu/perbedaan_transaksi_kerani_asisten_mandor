"""
SQLAlchemy Models untuk FFB Template System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BLOB, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .connection import Base

class ReportTemplate(Base):
    """
    Model untuk report templates
    """
    __tablename__ = 'REPORT_TEMPLATES'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), default='FFB_ANALYSIS')
    template_type = Column(String(50), default='JASPER')  # JASPER, HTML, EXCEL
    template_content = Column(BLOB)  # Jasper .jrxml content
    parameter_schema = Column(JSON)  # Parameter definition
    sql_query = Column(Text)  # Base SQL query dengan placeholders
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_by = Column(String(100))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)

    # Relationships
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")
    executions = relationship("TemplateExecution", back_populates="template")

    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"


class TemplateVersion(Base):
    """
    Model untuk template versioning
    """
    __tablename__ = 'TEMPLATE_VERSIONS'

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('REPORT_TEMPLATES.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    template_content = Column(BLOB)
    changelog = Column(Text)
    is_active = Column(Boolean, default=False)

    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    template = relationship("ReportTemplate", back_populates="versions")

    def __repr__(self):
        return f"<TemplateVersion(template_id={self.template_id}, version={self.version_number})>"


class TemplateExecution(Base):
    """
    Model untuk tracking template execution history
    """
    __tablename__ = 'TEMPLATE_EXECUTIONS'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(Integer, ForeignKey('REPORT_TEMPLATES.id'), nullable=False)

    # Execution parameters
    parameters = Column(JSON)  # Parameters yang digunakan
    estates = Column(JSON)  # Estates yang dipilih
    date_range = Column(JSON)  # Date range filter

    # Execution results
    status = Column(String(20), default='PENDING')  # PENDING, RUNNING, SUCCESS, ERROR
    execution_time = Column(Float)  # Execution time in seconds
    record_count = Column(Integer)  # Jumlah records yang diproses

    # Output
    output_file_path = Column(String(500))
    output_format = Column(String(20))  # PDF, EXCEL, HTML

    # Error handling
    error_message = Column(Text)

    # Metadata
    executed_by = Column(String(100))
    executed_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    # Relationships
    template = relationship("ReportTemplate", back_populates="executions")

    def __repr__(self):
        return f"<TemplateExecution(id={self.id}, template_id={self.template_id}, status='{self.status}')>"


class TemplateParameter(Base):
    """
    Model untuk template parameter definitions
    """
    __tablename__ = 'TEMPLATE_PARAMETERS'

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('REPORT_TEMPLATES.id'), nullable=False)
    name = Column(String(100), nullable=False)
    parameter_type = Column(String(50), nullable=False)  # STRING, DATE, NUMBER, LIST, ESTATE, DATE_RANGE
    display_name = Column(String(255))
    description = Column(Text)
    default_value = Column(String(500))
    is_required = Column(Boolean, default=False)
    validation_rule = Column(String(500))  # Regex atau validation expression

    # UI Configuration
    ui_component = Column(String(50), default='INPUT')  # INPUT, SELECT, DATE_PICKER, CHECKBOX
    options = Column(JSON)  # For SELECT or MULTI_SELECT
    order_index = Column(Integer, default=0)

    def __repr__(self):
        return f"<TemplateParameter(name='{self.name}', type='{self.parameter_type}')>"


class User(Base):
    """
    Model untuk user management
    """
    __tablename__ = 'USERS'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255))
    full_name = Column(String(255))
    password_hash = Column(String(255))

    # Roles dan permissions
    role = Column(String(50), default='USER')  # ADMIN, MANAGER, USER
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)

    # Estate access
    allowed_estates = Column(JSON)  # Estates yang bisa diakses

    # Metadata
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class SystemConfig(Base):
    """
    Model untuk system configuration
    """
    __tablename__ = 'SYSTEM_CONFIG'

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON)
    description = Column(Text)
    config_type = Column(String(50), default='GENERAL')  # GENERAL, JASPER, DATABASE, UI

    # Metadata
    updated_by = Column(String(100))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', type='{self.config_type}')>"


class AuditLog(Base):
    """
    Model untuk audit trail
    """
    __tablename__ = 'AUDIT_LOG'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('USERS.id'))
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, EXECUTE
    entity_type = Column(String(100))  # TEMPLATE, USER, CONFIG
    entity_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)

    # Request information
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Metadata
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', entity_type='{self.entity_type}')>"


# FFB Data Views (Read-only views untuk optimasi)
class FFBTransactionView(Base):
    """
    Read-only view untuk FFB transaction data
    """
    __tablename__ = 'FFB_TRANSACTION_VIEW'

    # Transaction fields
    transno = Column(String(50), primary_key=True)
    scanuserid = Column(String(50))
    recordtag = Column(String(10))  # PM, P1, P5
    transdate = Column(DateTime)
    fieldid = Column(Integer)
    afd = Column(String(10))
    block = Column(String(50))
    treecount = Column(Integer)
    bunchcount = Column(Integer)
    loosefruit = Column(Integer)
    weight = Column(Float)
    tbs = Column(Integer)
    harvester = Column(String(100))
    takenby = Column(String(100))

    # Reference data
    divid = Column(Integer)
    divname = Column(String(255))
    empname = Column(String(255))
    fieldname = Column(String(255))

    # Computed fields
    month_num = Column(Integer)  # Extracted from transdate
    estate_name = Column(String(255))

    __table_args__ = {'info': {'is_view': True}}


class FFBMonthlyTable(Base):
    """
    Model untuk tracking monthly table availability
    """
    __tablename__ = 'FFB_MONTHLY_TABLES'

    id = Column(Integer, primary_key=True)
    estate_name = Column(String(255), nullable=False)
    table_name = Column(String(50), nullable=False)  # FFBSCANNERDATA09
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Table statistics
    record_count = Column(Integer, default=0)
    has_pm_records = Column(Boolean, default=False)
    has_p1_records = Column(Boolean, default=False)
    has_p5_records = Column(Boolean, default=False)

    # Metadata
    last_analyzed = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<FFBMonthlyTable(estate='{self.estate_name}', table='{self.table_name}')>"


# Factory functions untuk model creation
def create_all_tables(engine):
    """
    Create all database tables

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")


def drop_all_tables(engine):
    """
    Drop all database tables (USE WITH CAUTION!)

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully")