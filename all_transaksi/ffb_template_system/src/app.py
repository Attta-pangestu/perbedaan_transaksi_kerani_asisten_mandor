"""
Main Flask Application untuk FFB Template System
"""

import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from flask_cors import CORS
from flask_login import LoginManager
from sqlalchemy import create_engine
import click

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_config, load_from_env
from src.core.database.connection import MultiEstateConnectionManager, create_multi_estate_manager
from src.core.database.models import Base

# Initialize extensions
login_manager = LoginManager()
multi_estate_manager = None

def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern

    Args:
        config_name: Configuration name (development, testing, production)

    Returns:
        Flask application instance
    """
    # Set template folder to src/web/templates
    template_folder = os.path.join(os.path.dirname(__file__), 'web', 'templates')
    app = Flask(__name__, template_folder=template_folder)

    # Load configuration
    config_class = get_config(config_name)
    load_from_env(app, config_class)
    app.config.from_object(config_class)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Setup logging
    setup_logging(app)

    # Initialize database
    init_database(app)

    # Setup error handlers
    register_error_handlers(app)

    # Initialize multi-estate connections
    init_multi_estate_connections(app)

    # Create upload directories
    create_directories(app)

    # Register context processor
    register_context_processor(app)

    # Create CLI commands
    create_cli_commands(app)

    app.logger.info(f"FFB Template System started with config: {config_name}")
    return app


def register_context_processor(app: Flask):
    """Register context processor for templates"""
    @app.context_processor
    def inject_config():
        """Inject global variables into templates"""
        return {
            'app_name': 'FFB Template System',
            'version': '1.0.0',
            'multi_estate_available': multi_estate_manager is not None
        }


def init_extensions(app: Flask):
    """Initialize Flask extensions"""
    global login_manager

    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'


def register_blueprints(app: Flask):
    """Register application blueprints"""
    from src.api.routes import api_bp
    from src.web.routes import web_bp

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix=app.config['API_PREFIX'])

    # Register web blueprint
    app.register_blueprint(web_bp)


def setup_logging(app: Flask):
    """Setup application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        log_dir = app.config['LOG_FILE'].parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Setup file handler with rotation
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('FFB Template System startup')


def init_database(app: Flask):
    """Initialize database"""
    try:
        # Create SQLAlchemy engine
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

        # Create tables
        Base.metadata.create_all(engine)

        app.logger.info("Database initialized successfully")

    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        raise


def init_multi_estate_connections(app: Flask):
    """Initialize multi-estate database connections"""
    global multi_estate_manager

    try:
        estate_config_path = app.config['ESTATE_CONFIG_PATH']
        if estate_config_path.exists():
            multi_estate_manager = create_multi_estate_manager(str(estate_config_path))
            app.logger.info(f"Multi-estate connections initialized: {len(multi_estate_manager.get_available_estates())} estates")
        else:
            app.logger.warning(f"Estate config file not found: {estate_config_path}")

    except Exception as e:
        app.logger.error(f"Multi-estate initialization failed: {e}")


def create_directories(app: Flask):
    """Create necessary directories"""
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['REPORTS_FOLDER'],
        app.config['TEMPLATES_FOLDER'],
        Path(app.config['LOG_FILE']).parent
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        app.logger.debug(f"Created directory: {directory}")


def register_error_handlers(app: Flask):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):  # Check if API request
            return {'error': 'Resource not found'}, 404
        return '404 Not Found', 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):  # Check if API request
            return {'error': 'Internal server error'}, 500
        return '500 Internal Server Error', 500

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):  # Check if API request
            return {'error': 'Access forbidden'}, 403
        return '403 Forbidden', 403

    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.path.startswith('/api/'):  # Check if API request
            return {'error': 'Unauthorized'}, 401
        return '401 Unauthorized', 401


# Make multi-estate manager available to other modules
def get_multi_estate_manager():
    """Get the global multi-estate manager instance"""
    return multi_estate_manager


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    from src.core.database.repositories import UserRepository
    from src.api.models.user import User

    with User.get_session() as session:
        repo = UserRepository(session)
        user_data = repo.get_user_by_id(int(user_id))
        if user_data:
            return User.from_orm(user_data)
    return None


# CLI commands
def create_cli_commands(app):
    """Create CLI commands for the application"""

    @app.cli.command()
    def init_db():
        """Initialize the database with default data"""
        click.echo("Initializing database...")
        # Create tables
        Base.metadata.create_all(create_engine(app.config['SQLALCHEMY_DATABASE_URI']))
        click.echo("Database tables created successfully.")

    @app.cli.command()
    def test_connections():
        """Test database connections"""
        click.echo("Testing database connections...")
        try:
            # Test basic database connection
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            with engine.connect() as conn:
                click.echo("✓ Application database connected")
        except Exception as e:
            click.echo(f"✗ Database connection failed: {e}")

    @app.cli.command()
    def create_sample_template():
        """Create a sample FFB template"""
        click.echo("Creating sample template...")
        click.echo("Sample template creation feature coming soon!")


# Create application instance
def create_application(config_name: str = None) -> Flask:
    """Create and configure Flask application"""
    return create_app(config_name)


# For development
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)