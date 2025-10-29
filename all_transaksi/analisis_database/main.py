#!/usr/bin/env python3
"""
FFB Scanner Analysis System - Main Application
Refactored modular system for multi-estate transaction analysis

This is the main entry point for the FFB Scanner Analysis System.
The system processes scanner transaction data from multiple estates to monitor
data entry quality and employee performance across three roles:
- Kerani (Scanner): Primary data entry personnel
- Mandor (Supervisor): Transaction verification
- Asisten (Assistant): Additional verification support

Author: Claude AI Assistant
Version: 2.0 (Refactored)
Date: 2025-10-27
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from datetime import date
from threading import Thread
from typing import List, Dict, Any, Optional, Tuple

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import services
from services.simple_configuration_service import SimpleConfigurationService
from services.validation_service import ValidationService
from services.analysis_service import AnalysisService
from services.report_generation_service import ReportGenerationService
from services.employee_performance_service import EmployeePerformanceService

# Import GUI
from gui.simple_main_window import SimpleMainWindow


class FFBAnalysisApp:
    """
    Main application class for FFB Scanner Analysis System
    """

    def __init__(self):
        """Initialize the application"""
        self.root = None
        self.main_window = None

        # Initialize services
        self.config_service = SimpleConfigurationService()
        self.validation_service = ValidationService()
        self.analysis_service = AnalysisService(self.config_service)
        self.report_service = ReportGenerationService()
        self.performance_service = EmployeePerformanceService()

        # Application state
        self.current_analysis = None
        self.is_analyzing = False

    def initialize(self):
        """Initialize the application"""
        try:
            # Create root window
            self.root = tk.Tk()
            self.root.title("FFB Scanner Analysis System v2.0 - Multi-Estate")
            self.root.geometry("1200x800")
            self.root.configure(bg='#f0f0f0')

            # Setup error handling
            self.root.report_callback_class = self.handle_error

            # Create main window
            self.main_window = SimpleMainWindow(
                self.root,
                self.config_service,
                self.validation_service,
                self.analysis_service,
                self.report_service,
                self.performance_service
            )

            # Start the GUI
            self.root.mainloop()

        except Exception as e:
            self.handle_critical_error(f"Failed to initialize application: {e}")

    def handle_error(self, exc_type, exc_value, exc_traceback):
        """Handle application errors"""
        error_msg = f"Error: {exc_type.__name__}: {exc_value}"
        print(error_msg)

        if self.main_window:
            self.main_window.show_error_message(error_msg)
        else:
            messagebox.showerror("Error", error_msg)

    def handle_critical_error(self, message: str):
        """Handle critical application errors"""
        print(f"CRITICAL ERROR: {message}")
        messagebox.showerror("Critical Error", message)
        sys.exit(1)

    def run_analysis(self, estate_configs: List[Tuple[str, str]],
                     start_date: date, end_date: date,
                     progress_callback=None) -> bool:
        """
        Run analysis with given parameters

        :param estate_configs: List of (estate_name, db_path) tuples
        :param start_date: Analysis start date
        :param end_date: Analysis end date
        :param progress_callback: Optional progress callback
        :return: True if successful, False otherwise
        """
        try:
            self.is_analyzing = True
            self.current_analysis = None

            # Validate parameters
            validation_result = self.validation_service.validate_analysis_parameters(
                estate_configs, start_date, end_date
            )

            if not validation_result['is_valid']:
                errors = '\n'.join(validation_result['errors'])
                self.show_error(f"Validation failed:\n{errors}")
                return False

            # Show warnings
            if validation_result['warnings']:
                warnings = '\n'.join(validation_result['warnings'])
                response = messagebox.askyesno(
                    "Validation Warnings",
                    f"Validation completed with warnings:\n\n{warnings}\n\nContinue with analysis?"
                )
                if not response:
                    return False

            # Run analysis
            def analysis_thread():
                try:
                    self.current_analysis = self.analysis_service.analyze_multiple_estates(
                        estate_configs=estate_configs,
                        start_date=start_date,
                        end_date=end_date,
                        progress_callback=progress_callback
                    )
                    self.root.after(0, self.on_analysis_complete)
                except Exception as e:
                    self.root.after(0, lambda: self.on_analysis_error(str(e)))

            # Start analysis in background thread
            thread = Thread(target=analysis_thread, daemon=True)
            thread.start()

            return True

        except Exception as e:
            self.show_error(f"Failed to start analysis: {e}")
            return False

    def on_analysis_complete(self):
        """Handle analysis completion"""
        self.is_analyzing = False
        if self.current_analysis:
            self.show_success("Analysis completed successfully!")
            # Auto-generate reports
            self.auto_generate_reports()

    def on_analysis_error(self, error_message: str):
        """Handle analysis error"""
        self.is_analyzing = False
        self.current_analysis = None
        self.show_error(f"Analysis failed: {error_message}")

    def auto_generate_reports(self):
        """Auto-generate reports after successful analysis"""
        if not self.current_analysis:
            return

        try:
            # Generate reports in multiple formats
            generated_files = self.report_service.generate_multi_format_reports(
                self.current_analysis
            )

            # Show results to user
            file_list = '\n'.join([f"• {file_type}: {filepath}"
                                   for file_type, filepath in generated_files.items()])

            self.show_info(f"Reports generated successfully:\n{file_list}")

        except Exception as e:
            self.show_error(f"Failed to generate reports: {e}")

    def show_error(self, message: str):
        """Show error message"""
        if self.main_window:
            self.main_window.show_error_message(message)
        else:
            messagebox.showerror("Error", message)

    def show_success(self, message: str):
        """Show success message"""
        if self.main_window:
            self.main_window.show_success_message(message)
        else:
            messagebox.showinfo("Success", message)

    def show_info(self, message: str):
        """Show info message"""
        if self.main_window:
            self.main_window.show_info_message(message)
        else:
            messagebox.showinfo("Information", message)

    def show_warning(self, message: str):
        """Show warning message"""
        if self.main_window:
            self.main_window.show_warning_message(message)
        else:
            messagebox.showwarning("Warning", message)

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Simple configuration service - no complex cleanup needed
            if self.config_service:
                logger.info("Simple configuration service cleanup complete")
            # Cleanup other resources if needed
        except Exception as e:
            print(f"Cleanup error: {e}")

    def shutdown(self):
        """Shutdown the application"""
        try:
            self.cleanup()
            if self.root:
                self.root.quit()
        except Exception as e:
            print(f"Shutdown error: {e}")
            sys.exit(1)


def main():
    """Main entry point"""
    try:
        # Check if required modules are available
        required_modules = [
            'tkinter', 'pandas', 'reportlab', 'tkcalendar'
        ]

        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            print("Missing required modules:")
            for module in missing_modules:
                print(f"  - {module}")
            print("\nPlease install missing modules:")
            print("pip install tkinter pandas reportlab tkcalendar")
            input("Press Enter to exit...")
            return

        # Create and run application
        app = FFBAnalysisApp()
        app.initialize()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()