"""
Configuration Management for FFB Template System
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Base configuration"""

    # Basic Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ffb_template.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload Configuration
    UPLOAD_FOLDER = Path('templates/uploads')
    REPORTS_FOLDER = Path('reports')
    TEMPLATES_FOLDER = Path('templates/jasper')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Estate Configuration
    ESTATE_CONFIG_PATH = Path('config.json')

    # Logging Configuration
    LOG_FILE = Path('logs/app.log')
    LOG_LEVEL = 'INFO'

    # API Configuration
    API_PREFIX = '/api'
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']

    # Jasper Configuration
    JASPER_COMPILER_PATH = os.environ.get('JASPER_COMPILER_PATH') or 'C:/Program Files/JasperSoft/jasperreports/lib'
    JASPER_TEMP_DIR = Path('temp/jasper')

    # Pagination
    ITEMS_PER_PAGE = 25

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Background Tasks
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    @staticmethod
    def init_app(app):
        """Initialize app with this configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'dev_ffb_template.db')

    # Allow larger files in development
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB

    # More verbose logging
    LOG_LEVEL = 'DEBUG'

    # Disable CSRF for easier development (enable in production)
    WTF_CSRF_ENABLED = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Suppress logging
    LOG_LEVEL = 'WARNING'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Production database (configure with environment variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'prod_ffb_template.db')

    # Enhanced security
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY

    # Security headers and settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Stricter file upload limits
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB

    # Production CORS origins
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Setup production logging
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')

            file_handler = RotatingFileHandler(
                cls.LOG_FILE,
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('FFB Template System production startup')


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])


def load_from_env(app, config_class):
    """Load configuration from environment variables"""
    # Override any config values from environment variables
    env_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'SQLALCHEMY_DATABASE_URI',
        'JASPER_COMPILER_PATH',
        'CELERY_BROKER_URL',
        'CELERY_RESULT_BACKEND',
        'CACHE_TYPE',
        'LOG_LEVEL'
    ]

    for var in env_vars:
        value = os.environ.get(var)
        if value:
            setattr(config_class, var, value)


# Make config available for import
__all__ = ['Config', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig', 'get_config', 'load_from_env']