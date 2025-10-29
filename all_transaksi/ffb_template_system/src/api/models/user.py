"""
User Model for FFB Template System
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.core.database.models import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='USER')  # ADMIN, MANAGER, USER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    preferences = Column(Text, nullable=True)  # JSON string for user preferences

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    @classmethod
    def get_session(cls):
        """Get database session for User model"""
        from src.config import get_config
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        config = get_config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()

    @classmethod
    def from_orm(cls, orm_user):
        """Create User instance from ORM object"""
        if orm_user is None:
            return None
        return cls(
            id=orm_user.id,
            username=orm_user.username,
            email=orm_user.email,
            full_name=orm_user.full_name,
            password_hash=orm_user.password_hash,
            role=orm_user.role,
            is_active=orm_user.is_active,
            created_at=orm_user.created_at,
            updated_at=orm_user.updated_at,
            last_login=orm_user.last_login,
            preferences=orm_user.preferences
        )

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'ADMIN'

    def is_manager(self):
        """Check if user is manager or admin"""
        return self.role in ['ADMIN', 'MANAGER']