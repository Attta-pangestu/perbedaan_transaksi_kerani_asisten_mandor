#!/usr/bin/env python3
"""
Main Entry Point for Modular Report System
Launches the GUI application with all integrated components
"""

import sys
import os
import logging
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from presentation.main_report_window import MainReportWindow
    from infrastructure.exceptions.custom_exceptions import ModularReportSystemError
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed and the project structure is correct.")
    sys.exit(1)


def setup_logging():
    """Setup logging configuration"""
    log_dir = current_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "modular_report_system.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'tkinter',
        'pandas',
        'reportlab',
        'openpyxl'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Missing required modules: {', '.join(missing_modules)}\n"
        error_msg += "Please install them using: pip install " + " ".join(missing_modules)
        raise ModularReportSystemError(error_msg)


def check_configuration():
    """Check if configuration files exist"""
    config_file = current_dir.parent / "config.json"
    
    if not config_file.exists():
        # Try to find config in parent directories
        for parent in current_dir.parents:
            potential_config = parent / "config.json"
            if potential_config.exists():
                config_file = potential_config
                break
        else:
            raise ModularReportSystemError(
                f"Configuration file not found. Expected at: {config_file}\n"
                "Please ensure config.json exists with estate configurations."
            )
    
    return str(config_file)


def main():
    """Main application entry point"""
    logger = setup_logging()
    logger.info("Starting Modular Report System")
    
    try:
        # Check dependencies
        logger.info("Checking dependencies...")
        check_dependencies()
        logger.info("All dependencies available")
        
        # Check configuration
        logger.info("Checking configuration...")
        config_path = check_configuration()
        logger.info(f"Configuration found at: {config_path}")
        
        # Create and run GUI application
        logger.info("Initializing GUI application...")
        root = tk.Tk()
        
        # Set application icon if available
        icon_path = current_dir.parent / "assets" / "logo_rebinmas.jpeg"
        if icon_path.exists():
            try:
                # For Windows, we might need to convert to .ico format
                # For now, just log that icon is available
                logger.info(f"Application icon available at: {icon_path}")
            except Exception as e:
                logger.warning(f"Could not set application icon: {e}")
        
        # Initialize main window
        app = MainReportWindow(root, config_path=config_path)
        
        # Configure root window
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        logger.info("GUI application initialized successfully")
        logger.info("Starting main event loop...")
        
        # Start the GUI event loop
        root.mainloop()
        
        logger.info("Application closed normally")
        
    except ModularReportSystemError as e:
        error_msg = f"System Error: {str(e)}"
        logger.error(error_msg)
        
        # Show error dialog if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Modular Report System Error", error_msg)
            root.destroy()
        except:
            print(error_msg)
        
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Show error dialog if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror("Unexpected Error", error_msg)
            root.destroy()
        except:
            print(error_msg)
        
        sys.exit(1)


if __name__ == "__main__":
    main()