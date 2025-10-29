#!/usr/bin/env python3
"""
Main GUI Application for Refactored FFB Analysis System
Refactored modular architecture with improved maintainability and separation of concerns.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import os
import sys
from datetime import datetime, date
import threading
import json

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from core.database import DatabaseManager, EstateConfig
    from analysis.ffb_analyzer import FFBAnalyzer
    from reporting.pdf_generator import PDFReportGenerator, ReportConfig
    from gui.components import EstateConfigFrame, DateRangeFrame, ProgressFrame, ResultsFrame, ButtonFrame
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Parent directory: {parent_dir}")
    raise


class MainApplication:
    """
    Main application class for FFB Analysis System.
    Coordinates between GUI, database management, analysis engine, and report generation.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the main application.

        Args:
            root: Root tkinter window
        """
        self.root = root
        self.estate_config = EstateConfig()
        self.db_manager = DatabaseManager(self.estate_config.estates)
        self.analyzer = FFBAnalyzer(self.db_manager)
        self.report_generator = PDFReportGenerator()

        self.setup_ui()
        self.load_estate_configuration()

    def setup_ui(self):
        """Setup the main user interface."""
        # Configure root window
        self.root.title("LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN - Refactored System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # Results frame gets expandable space

        # Create UI components
        self.create_title_section(main_frame)
        self.estate_frame = EstateConfigFrame(main_frame, self.estate_config)
        self.date_frame = DateRangeFrame(main_frame)
        self.progress_frame = ProgressFrame(main_frame)
        self.results_frame = ResultsFrame(main_frame)
        self.button_frame = ButtonFrame(main_frame)

        # Grid layout
        self.estate_frame.frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.date_frame.frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.progress_frame.frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.results_frame.frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        self.button_frame.frame.grid(row=5, column=0, pady=20)

    def create_title_section(self, parent_frame):
        """Create title section."""
        title_label = ttk.Label(
            parent_frame,
            text="SISTEM ANALISIS FFB MULTI-ESTATE (REFACTORED)",
            font=('Arial', 16, 'bold'),
            foreground='#1A365D'
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

    def load_estate_configuration(self):
        """Load and display estate configuration."""
        self.estate_frame.load_estates(self.estate_config.estates)

    def start_analysis(self):
        """Start the analysis process in a separate thread."""
        selected_estates = self.estate_frame.get_selected_estates()
        if not selected_estates:
            messagebox.showerror("Error", "Silakan pilih minimal satu estate")
            return

        start_date = self.date_frame.get_start_date()
        end_date = self.date_frame.get_end_date()

        if start_date > end_date:
            messagebox.showerror("Error Tanggal", "Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
            return

        # Start analysis in background thread
        thread = threading.Thread(
            target=self.run_analysis_threaded,
            args=(selected_estates, start_date, end_date)
        )
        thread.daemon = True
        thread.start()

    def run_analysis_threaded(self, selected_estates, start_date, end_date):
        """
        Run analysis in background thread with proper error handling.

        Args:
            selected_estates: List of selected estate names
            start_date: Analysis start date
            end_date: Analysis end date
        """
        try:
            self.progress_frame.set_status("Memulai analisis...")
            self.progress_frame.set_progress(0, len(selected_estates))

            # Check if we should use the 704 filter (for May 2025)
            use_status_704_filter = self._should_use_704_filter(start_date, end_date)

            results = self.analyzer.analyze_multiple_estates(
                selected_estates, start_date, end_date, use_status_704_filter
            )

            if results and '_summary' in results:
                summary = results['_summary']
                self.progress_frame.set_status("Membuat laporan PDF...")
                self.results_frame.log_message(f"✓ Analisis selesai: {summary.get('successful_estates', 0)}/{len(selected_estates)} estate berhasil")

                # Generate PDF report
                try:
                    pdf_path = self.report_generator.create_multi_estate_report(
                        results, start_date, end_date
                    )
                    self.results_frame.log_message(f"✓ Laporan PDF dibuat: {os.path.basename(pdf_path)}")
                    self.progress_frame.set_status("Analisis selesai")
                    self.progress_frame.set_progress(100, 100)

                except Exception as e:
                    self.results_frame.log_message(f"✗ Error membuat PDF: {str(e)}")
                    self.progress_frame.set_status("Error generating PDF")
            else:
                self.results_frame.log_message("✗ Tidak ada hasil untuk ditampilkan")
                self.progress_frame.set_status("Tidak ada data ditemukan")

        except Exception as e:
            error_msg = f"Error dalam analisis: {str(e)}"
            self.results_frame.log_message(f"✗ {error_msg}")
            self.progress_frame.set_status("Error")
            messagebox.showerror("Error Analisis", error_msg)

    def _should_use_704_filter(self, start_date: date, end_date: date) -> bool:
        """
        Determine if the special TRANSSTATUS 704 filter should be used.

        Args:
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            True if filter should be used, False otherwise
        """
        # Check if the date range includes May 2025
        may_2025 = date(2025, 5, 1)
        may_end_2025 = date(2025, 5, 31)

        # Check for overlap with May 2025
        start_overlaps = start_date <= may_end_2025
        end_overlaps = end_date >= may_2025

        return start_overlaps and end_overlaps

    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_dir = self.report_generator.output_dir
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showinfo("Info", f"Folder output tidak ditemukan: {output_dir}")

    def clear_results(self):
        """Clear the results display."""
        self.results_frame.clear_results()
        self.progress_frame.set_status("Siap untuk menganalisis")
        self.progress_frame.set_progress(0, 0)

    def show_about(self):
        """Show about dialog."""
        about_text = """SISTEM ANALISIS FFB MULTI-ESTATE v2.0 (REFACTORED)

Versi refactored dengan arsitektur modular:
• Database Management Layer
• Analysis Engine Layer
• Report Generation Layer
• GUI Component Layer

Fitur:
• Multi-estate analysis
• Real-time data verification
• Professional PDF reporting
• Enhanced error handling
• Modular architecture

Dikembangkan oleh: Claude AI Assistant
Untuk: PT. Rebinmas Jaya"""

        messagebox.showinfo("Tentang Aplikasi", about_text)

    def run(self):
        """Start the main application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi error: {str(e)}")


def main():
    """Main entry point for the application."""
    try:
        # Create root window
        root = tk.Tk()

        # Create and run application
        app = MainApplication(root)
        app.run()

    except Exception as e:
        messagebox.showerror("Startup Error", f"Gagal memulai aplikasi: {str(e)}")


if __name__ == "__main__":
    main()