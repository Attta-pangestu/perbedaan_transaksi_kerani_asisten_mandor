#!/usr/bin/env python3
"""
Start script untuk Sistem Laporan FFB dengan Template Manager
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Add parent directory to path for firebird_connector
parent_path = Path(__file__).parent
sys.path.insert(0, str(parent_path))

# Change to src directory for relative imports
os.chdir(src_path)

def setup_logging():
    """Setup logging configuration"""
    logs_dir = Path("../logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'app.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check required dependencies"""
    try:
        import tkinter
        print("[OK] tkinter available")
    except ImportError:
        print("[ERROR] tkinter not available")
        return False

    try:
        from tkcalendar import DateEntry
        print("[OK] tkcalendar available")
    except ImportError:
        print("[ERROR] tkcalendar not available - install with: pip install tkcalendar")
        return False

    try:
        import pandas
        print("[OK] pandas available")
    except ImportError:
        print("[ERROR] pandas not available - install with: pip install pandas")
        return False

    try:
        from reportlab.platypus import SimpleDocTemplate
        print("[OK] reportlab available")
    except ImportError:
        print("[ERROR] reportlab not available - install with: pip install reportlab")
        return False

    # Check firebird_connector.py exists
    firebird_connector_path = Path("../firebird_connector.py")
    print(f"Looking for firebird_connector at: {firebird_connector_path.absolute()}")
    if firebird_connector_path.exists():
        print("[OK] firebird_connector.py found")
    else:
        print("[ERROR] firebird_connector.py not found")
        # Try other paths
        other_paths = [
            Path("../../firebird_connector.py"),
            Path("firebird_connector.py")
        ]
        for other_path in other_paths:
            print(f"Trying: {other_path.absolute()}")
            if other_path.exists():
                print(f"[OK] Found at: {other_path.absolute()}")
                break
        else:
            print("[ERROR] firebird_connector.py not found in any location")
            return False

    return True

def main():
    """Main entry point"""
    print("=" * 60)
    print("SISTEM LAPORAN VERIFIKASI FFB - TEMPLATE MANAGER")
    print("=" * 60)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install required packages:")
        print("pip install tkcalendar pandas reportlab")
        input("Press Enter to exit...")
        return False

    print("\n[SUCCESS] All dependencies satisfied!")

    # Check config file
    config_path = Path("../config.json")
    if config_path.exists():
        print("[OK] Configuration file found")
    else:
        print("[WARNING] Configuration file not found - will use defaults")

    print("\n[STARTING] Starting application...")

    try:
        # Import and start GUI
        from main_gui import main as start_gui
        start_gui()
        return True
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"\n[ERROR] Error starting application: {e}")
        input("Press Enter to exit...")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)