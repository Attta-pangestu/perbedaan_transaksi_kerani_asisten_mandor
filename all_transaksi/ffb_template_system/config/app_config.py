"""
Application Configuration untuk FFB Template System
"""

import os
from pathlib import Path
from datetime import timedelta

# Base directory
BASE_DIR = Path(__file__).parent.parent

class Config:
    """Base configuration"""

    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ffb_template_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Multi-Estate Database Configuration
    ESTATE_CONFIG_PATH = BASE_DIR.parent / "config.json"

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / "data" / "uploads"
    REPORTS_FOLDER = BASE_DIR / "data" / "reports"
    TEMPLATES_FOLDER = BASE_DIR / "jasper_templates"

    # Jasper Reports Configuration
    JASPER_HOME = os.environ.get('JASPER_HOME') or ''
    JAVA_HOME = os.environ.get('JAVA_HOME') or ''

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = BASE_DIR / "logs" / "app.log"

    # CORS Configuration
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:5000"]

    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 100

    # Security
    BCRYPT_LOG_ROUNDS = 12
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Email Configuration (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Redis Configuration (for background tasks)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Background Tasks
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'

    # Template Configuration
    TEMPLATE_CACHE_SIZE = 100
    TEMPLATE_CACHE_TIMEOUT = 3600  # 1 hour

    # Report Configuration
    DEFAULT_REPORT_FORMAT = 'pdf'
    REPORT_CACHE_TIMEOUT = 1800  # 30 minutes

    # User Configuration
    DEFAULT_USER_ROLE = 'USER'
    ADMIN_EMAILS = os.environ.get('ADMIN_EMAILS', '').split(',') if os.environ.get('ADMIN_EMAILS') else []

    # Development/Production Flags
    DEBUG = False
    TESTING = False

    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        # Create necessary directories
        directories = [
            Config.UPLOAD_FOLDER,
            Config.REPORTS_FOLDER,
            Config.TEMPLATES_FOLDER,
            Config.LOG_FILE.parent
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

    # Allow all origins in development
    CORS_ORIGINS = ["*"]

    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "data" / "dev_ffb_template.db"}'

    # Logging
    LOG_LEVEL = 'DEBUG'

    # Disable CSRF protection in development
    WTF_CSRF_ENABLED = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Use shorter token lifetimes for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=10)

    # Logging
    LOG_LEVEL = 'WARNING'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Use environment variables for production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///production_ffb_template.db'

    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Logging
    LOG_LEVEL = 'INFO'

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []

    # Enable CSRF protection
    WTF_CSRF_ENABLED = True

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'memory://'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Get configuration class by name

    Args:
        config_name: Configuration name (development, testing, production)

    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])


def load_from_env(app, config_class: Config):
    """
    Load configuration from environment variables

    Args:
        app: Flask application instance
        config_class: Configuration class
    """
    # Load all uppercase variables from environment
    for key in dir(config_class):
        if key.isupper() and not key.startswith('_'):
            env_value = os.environ.get(key)
            if env_value is not None:
                # Convert string values to appropriate types
                if env_value.lower() in ('true', 'false'):
                    setattr(config_class, key, env_value.lower() == 'true')
                elif env_value.isdigit():
                    setattr(config_class, key, int(env_value))
                elif env_value.replace('.', '').isdigit():
                    setattr(config_class, key, float(env_value))
                else:
                    setattr(config_class, key, env_value)

    # Update Flask app config
    app.config.from_object(config_class)