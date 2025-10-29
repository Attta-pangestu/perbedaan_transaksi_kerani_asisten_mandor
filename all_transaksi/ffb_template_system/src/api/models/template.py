"""
Template Model for FFB Template System
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database.models import Base


class ReportTemplate(Base):
    """Report template model"""
    __tablename__ = 'report_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # FFB_ANALYSIS, EMPLOYEE_PERFORMANCE, etc.
    template_type = Column(String(20), default='JASPER')  # JASPER, HTML, EXCEL
    sql_query = Column(Text, nullable=False)
    parameter_schema = Column(Text, nullable=True)  # JSON string
    jasper_template = Column(String(500), nullable=True)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ReportTemplate {self.name}>'

    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'template_type': self.template_type,
            'sql_query': self.sql_query,
            'parameter_schema': self.parameter_schema,
            'jasper_template': self.jasper_template,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_session(cls):
        """Get database session for ReportTemplate model"""
        from src.config import get_config
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        config = get_config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()

    @classmethod
    def from_orm(cls, orm_template):
        """Create ReportTemplate instance from ORM object"""
        if orm_template is None:
            return None
        return cls(
            id=orm_template.id,
            name=orm_template.name,
            description=orm_template.description,
            category=orm_template.category,
            template_type=orm_template.template_type,
            sql_query=orm_template.sql_query,
            parameter_schema=orm_template.parameter_schema,
            jasper_template=orm_template.jasper_template,
            is_public=orm_template.is_public,
            is_active=orm_template.is_active,
            created_by=orm_template.created_by,
            created_at=orm_template.created_at,
            updated_at=orm_template.updated_at
        )