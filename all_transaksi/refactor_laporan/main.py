"""
FFB Scanner Analysis System - Main Entry Point

Main application entry point untuk FFB (Fresh Fruit Bunch) Scanner Analysis System
yang telah direfaktor dengan arsitektur modular.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import core modules
try:
    from core.config import FFBConfig
    from core.business_logic import FFBVerificationEngine, FFBDataProcessor
    from database.firebird_connector import FirebirdConnector
    from database.query_builder import FFBQueryBuilder
    from analysis.verification_engine import FFBVerificationEngine as AnalysisEngine
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all dependencies are installed and paths are correct")
    sys.exit(1)

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"ffb_analysis_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

logger = setup_logging()

class FFBAnalysisSystem:
    """
    Main system class yang mengoordinasikan semua komponen
    """

    def __init__(self):
        """
        Initialize FFB Analysis System
        """
        logger.info("Initializing FFB Analysis System...")

        # Load configuration
        self.config = FFBConfig()

        # Initialize core components
        self.data_processor = FFBDataProcessor()
        self.verification_engine = FFBVerificationEngine(self.config.analysis_config)
        self.query_builder = FFBQueryBuilder()

        # Database connectors akan diinisialisasi per estate saat dibutuhkan
        self.db_connectors = {}

        logger.info("FFB Analysis System initialized successfully")

    def get_database_connector(self, estate_name: str) -> FirebirdConnector:
        """
        Get atau create database connector untuk estate tertentu

        Args:
            estate_name: Nama estate

        Returns:
            FirebirdConnector instance
        """
        if estate_name not in self.db_connectors:
            db_path = self.config.get_estate_path(estate_name)
            if not db_path:
                raise ValueError(f"No database path configured for estate: {estate_name}")

            connector = FirebirdConnector(db_path=db_path, use_localhost=True)
            self.db_connectors[estate_name] = connector

        return self.db_connectors[estate_name]

    def test_all_connections(self) -> dict:
        """
        Test koneksi database untuk semua estates

        Returns:
            Dict dengan test results per estate
        """
        logger.info("Testing all database connections...")

        results = {}
        estates = self.config.get_all_estates()

        for estate_name in estates:
            try:
                connector = self.get_database_connector(estate_name)
                is_connected = connector.test_connection()
                results[estate_name] = {
                    'connected': is_connected,
                    'path': self.config.get_estate_path(estate_name),
                    'error': None
                }
            except Exception as e:
                results[estate_name] = {
                    'connected': False,
                    'path': self.config.get_estate_path(estate_name),
                    'error': str(e)
                }

        logger.info(f"Connection test complete: {sum(1 for r in results.values() if r['connected'])}/{len(results)} connected")
        return results

    def run_gui(self):
        """
        Jalankan aplikasi GUI
        """
        logger.info("Starting GUI application...")

        try:
            # Import GUI module here to avoid import issues if GUI is not needed
            from gui.main_application import MultiEstateFFBAnalysisGUI
            app = MultiEstateFFBAnalysisGUI(self.config, self)
            app.run()
        except Exception as e:
            logger.error(f"Error starting GUI: {e}")
            raise


def main():
    """
    Main entry point function
    """
    try:
        # Initialize system
        system = FFBAnalysisSystem()

        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--test-connections':
                # Test database connections
                results = system.test_all_connections()
                print("\nDatabase Connection Test Results:")
                print("=" * 50)
                for estate, result in results.items():
                    status = "✓ Connected" if result['connected'] else "✗ Failed"
                    print(f"{estate}: {status}")
                    if result['error']:
                        print(f"  Error: {result['error']}")
                return

            elif sys.argv[1] == '--help':
                print("FFB Scanner Analysis System")
                print("Usage:")
                print("  python main.py              # Start GUI")
                print("  python main.py --test-connections  # Test database connections")
                print("  python main.py --help       # Show this help")
                return

        # Default: start GUI
        system.run_gui()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()