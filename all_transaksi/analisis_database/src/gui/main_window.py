"""
Main Window
Main application window for FFB Analysis System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import List, Dict, Any, Optional, Tuple

from gui.widgets.simple_estate_selection_widget import SimpleEstateSelectionWidget
from gui.widgets.date_range_widget import DateRangeWidget
from gui.widgets.progress_widget import ProgressWidget
from gui.widgets.results_display_widget import ResultsDisplayWidget
from gui.widgets.report_export_widget import ReportExportWidget

from services.simple_configuration_service import SimpleConfigurationService
from services.validation_service import ValidationService
from services.analysis_service import AnalysisService
from services.report_generation_service import ReportGenerationService
from services.employee_performance_service import EmployeePerformanceService


class MainWindow:
    """
    Main application window for FFB Analysis System
    """

    def __init__(self, root: tk.Tk,
                 config_service: SimpleConfigurationService,
                 validation_service: ValidationService,
                 analysis_service: AnalysisService,
                 report_service: ReportGenerationService,
                 performance_service: EmployeePerformanceService):
        """
        Initialize main window

        :param root: Tkinter root window
        :param config_service: Configuration service
        :param validation_service: Validation service
        :param analysis_service: Analysis service
        :param report_service: Report generation service
        :param performance_service: Employee performance service
        """
        self.root = root
        self.config_service = config_service
        self.validation_service = validation_service
        self.analysis_service = analysis_service
        self.report_service = report_service
        self.performance_service = performance_service

        # Application state
        self.current_analysis = None
        self.is_analyzing = False

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the main window UI"""
        # Configure root window
        self.root.configure(bg='#f0f0f0')

        # Create main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_container,
            text="SISTEM ANALISIS FFB SCANNER MULTI-ESTATE",
            font=('Arial', 16, 'bold'),
            foreground='#2E4057'
        )
        title_label.pack(pady=(0, 20))

        # Create main content area with notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create tabs
        self.create_main_tab()
        self.create_configuration_tab()
        self.create_reports_tab()
        self.create_help_tab()

        # Status bar
        self.create_status_bar(main_container)

        # Menu bar
        self.create_menu_bar()

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New Analysis", command=self.new_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="Export Analysis", command=self.export_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        tools_menu.add_command(label="Validate All Estates", command=self.validate_all_estates)
        tools_menu.add_command(label="Test Connections", command=self.test_connections)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Reports", command=self.clear_reports)
        tools_menu.add_command(label="Backup Configuration", command=self.backup_configuration)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)

    def create_main_tab(self):
        """Create main analysis tab"""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Analysis")

        # Estate selection - simple version
        self.estate_widget = SimpleEstateSelectionWidget(
            main_tab,
            self.config_service,
            self.validation_service,
            on_selection_changed=self.on_estate_selection_changed
        )
        self.estate_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Date range selection
        self.date_widget = DateRangeWidget(
            main_tab,
            on_date_changed=self.on_date_range_changed
        )
        self.date_widget.pack(fill=tk.X, pady=(0, 10))

        # Progress widget
        self.progress_widget = ProgressWidget(main_tab)
        self.progress_widget.pack(fill=tk.X, pady=(0, 10))

        # Results display
        self.results_widget = ResultsDisplayWidget(main_tab)
        self.results_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Analysis controls
        controls_frame = ttk.Frame(main_tab)
        controls_frame.pack(fill=tk.X)

        ttk.Button(
            controls_frame,
            text="Mulai Analisis Estate",
            command=self.start_analysis
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="Analisis Estate Terpilih",
            command=self.start_selected_analysis
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="Hapus Hasil",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="Buka Folder Reports",
            command=self.open_reports_folder
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="Stop Analysis",
            command=self.stop_analysis,
            state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=5)

        self.stop_button = controls_frame.winfo_children()[-1]  # Reference to stop button

    def create_configuration_tab(self):
        """Create configuration tab"""
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="Configuration")

        # Configuration controls will be added here
        ttk.Label(
            config_tab,
            text="Configuration management features will be added here",
            font=('Arial', 12)
        ).pack(expand=True)

    def create_reports_tab(self):
        """Create reports tab"""
        reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(reports_tab, text="Reports")

        # Report controls
        self.report_widget = ReportExportWidget(
            reports_tab,
            self.report_service
        )
        self.report_widget.pack(fill=tk.BOTH, expand=True)

    def create_help_tab(self):
        """Create help tab"""
        help_tab = ttk.Frame(self.notebook)
        self.notebook.add(help_tab, text="Help")

        # Help content
        help_text = """
        FFB SCANNER ANALYSIS SYSTEM - HELP

        SELAMAT DATANG DI ANALISIS:
        1. Pilih estate yang akan dianalisis pada tab "Analysis"
        2. Tentukan rentang tanggal dengan Date Range widget
        3. Gunakan "Mulai Analisis Estate" untuk menganalisis semua estate
        4. Gunakan "Analisis Estate Terpilih" untuk menganalisis hanya estate yang dipilih

        METRIK YANG DIANALISIS:
        • Kerani: % transaksi yang sudah diverifikasi dari total yang dibuat
        • Mandor/Asisten: % transaksi yang dibandingkan dengan total Kerani
        • Perbedaan Input: Jumlah field yang berbeda antara input Kerani dan verifikator
        • Tingkat Verifikasi: Persentase transaksi yang sudah terverifikasi
        • Tingkat Perbedaan: Persentase transaksi dengan perbedaan input data

        FIELD YANG DIBANDING:
        • RIPEBCH (Tandan Masak)
        • UNRIPEBCH (Tandan Mentah)
        • BLACKBCH (Tandan Hitam)
        • ROTTENBCH (Tandan Busuk)
        • LONGSTALKBCH (Tandan Tangkai Panjang)
        • RATDMGBCH (Tanda Rusak Tikus)
        • LOOSEFRUIT (Buah Jatuh)

        STATUS FILTER KHUSUS:
        Filter TRANSSTATUS 704 diterapkan otomatis untuk analisis bulan Mei 2025
        untuk meningkatkan akurasi data yang sudah terverifikasi.

        LANGKAH ANALISIS:
        1. Extract transaksi dari tabel bulanan FFBSCANNERDATA[MM]
        2. Grup berdasarkan TRANSNO untuk menemukan duplikat
        3. Verifikasi: PM (Kerani) + P1/P5 (Mandor/Asisten) = Terverifikasi
        4. Hitung metrik kinerja per karyawan
        5. Generate laporan PDF dan Excel

        TIPS PENGGUNAAN:
        • Pastikan semua estate terhubung sebelum memulai analisis
        • Pilih rentang tanggal yang reasonable (maksimal 1 tahun)
        • Monitor progress bar untuk melihat status analisis
        • Periksa hasil analisis di tab "Reports" setelah selesai
        • Backup konfigurasi secara berkala

        TROUBLESHOOTING:
        • Koneksi gagal: Periksa path database dan koneksi Firebird
        • Tidak ada data: Pastikan tanggal range sesuai dengan data yang ada
        • Error validasi: Periksa format tanggal dan pilihan estate
        • Report gagal: Periksa folder output dan izin menulis

        KONTAK SUPPORT:
        Email: support@rebinmasjaya.com
        Phone: [Nomor Telepon IT]
        """

        help_text_widget = tk.Text(
            help_tab,
            wrap=tk.WORD,
            width=80,
            height=30,
            font=('Courier', 10)
        )
        help_text_widget.pack(padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)

        # Create scrollable text widget
        text_frame = ttk.Frame(help_tab)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Arial', 9),
            yscrollcommand=scrollbar.set
        )
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=help_text.yview)

        help_text.insert(tk.END, help_text)
        help_text.config(state=tk.DISABLED)

    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready - Pilih estate dan tentukan tanggal untuk memulai analisis",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, padx=5)

        # Connection status
        self.connection_status = ttk.Label(
            status_frame,
            text="0/0 estates connected",
            relief=tk.SUNKEN,
            anchor=tk.E
        )
        self.connection_status.pack(side=tk.RIGHT, padx=5)

    def new_analysis(self):
        """Start new analysis setup"""
        # Reset selections
        self.estate_widget.clear_estate_selection()
        self.date_widget.select_current_month()
        self.results_widget.clear_results()
        self.progress_widget.reset()

        # Switch to analysis tab
        self.notebook.select(0)

    def start_analysis(self):
        """Start analysis for all valid estates"""
        if self.is_analyzing:
            self.show_warning("Analysis sedang berjalan. Tunggu hingga selesai.")
            return

        # Get all valid estates
        estate_configs = self.estate_widget.get_valid_selected_estates()

        if not estate_configs:
            self.show_warning("Tidak ada estate valid yang dipilih. Silakan pilih estate yang terhubung.")
            return

        # Get date range
        start_date, end_date = self.date_widget.get_date_range()

        # Validate date range
        if not self.date_widget.validate_date_range():
            return

        # Show confirmation dialog
        result = messagebox.askyesno(
            "Konfirmasi Analisis",
            f"Akan menganalisis {len(estate_configs)} estate:\n\n"
            f"Periode: {self.date_widget.get_date_range_string()}\n\n"
            f"Analisis akan berjalan di background. Lanjutkan?"
        )

        if result:
            self._start_analysis_thread(estate_configs, start_date, end_date)

    def start_selected_analysis(self):
        """Start analysis for selected estates only"""
        if self.is_analyzing:
            self.show_warning("Analysis sedang berjalan. Tunggu hingga selesai.")
            return

        # Get selected estates (all, not just valid ones)
        estate_configs = self.estate_widget.get_selected_estates()

        if not estate_configs:
            self.show_warning("Tidak ada estate yang dipilih.")
            return

        # Get date range
        start_date, end_date = self.date_widget.get_date_range()

        # Validate date range
        if not self.date_widget.validate_date_range():
            return

        # Show warning if some estates may not be valid
        valid_configs = self.estate_widget.get_valid_selected_estates()
        if len(valid_configs) < len(estate_configs):
            result = messagebox.askyesno(
                "Peringatan Estate",
                f"Dari {len(estate_configs)} estate yang dipilih, "
                f"hanya {len(valid_configs)} yang valid.\n\n"
                "Estate yang tidak valid akan dilewati dalam analisis.\n\n"
                "Lanjutkan?"
            )

            if not result:
                return

            # Use only valid estates
            estate_configs = valid_configs

        # Show confirmation dialog
        result = messagebox.askyesno(
            "Konfirmasi Analisis",
            f"Akan menganalisis {len(estate_configs)} estate terpilih:\n\n"
            f"Periode: {self.date_widget.get_date_range_string()}\n\n"
            "Analisis akan berjalan di background. Lanjutkan?"
        )

        if result:
            self._start_analysis_thread(estate_configs, start_date, end_date)

    def _start_analysis_thread(self, estate_configs: List[Tuple[str, str]],
                           start_date: date, end_date: date):
        """Start analysis in background thread"""
        self.is_analyzing = True
        self.stop_button.config(state=tk.NORMAL)

        # Update UI
        self.update_status("Memulai analisis...")
        self.progress_widget.set_max_progress(len(estate_configs))
        self.results_widget.clear_results()

        # Create progress callback
        def progress_callback(current, total, message):
            self.root.after(0, lambda: self.update_progress(current, total, message))

        try:
            # Run analysis
            self.current_analysis = self.analysis_service.analyze_multiple_estates(
                estate_configs=estate_configs,
                start_date=start_date,
                end_date=end_date,
                progress_callback=progress_callback
            )

            # Handle completion in main thread
            self.root.after(0, self.on_analysis_complete)

        except Exception as e:
            # Handle error in main thread
            self.root.after(0, lambda: self.on_analysis_error(str(e)))

    def stop_analysis(self):
        """Stop current analysis"""
        if not self.is_analyzing:
            self.show_info("Tidak ada analisis yang sedang berjalan.")
            return

        result = messagebox.askyesno(
            "Hentikan Analisis",
            "Apakah Anda yakin ingin menghentikan analisis yang sedang berjalan?"
        )

        if result:
            self.is_analyzing = False
            self.stop_button.config(state=tk.DISABLED)
            self.update_status("Analisis dihentikan oleh pengguna")
            self.progress_widget.set_status("Dihentikan")

    def on_analysis_complete(self):
        """Handle analysis completion"""
        self.is_analyzing = False
        self.stop_button.config(state=tk.DISABLED)

        if self.current_analysis:
            # Update results
            self.results_widget.display_analysis_result(self.current_analysis)
            self.progress_widget.set_progress(
                self.progress_widget.get_max_progress(),
                self.progress_widget.get_max_progress()
            )
            self.progress_widget.set_status("Selesai")

            # Update status
            total_divisions = self.current_analysis.total_divisions
            verification_rate = self.current_analysis.grand_verification_rate
            self.update_status(
                f"Analysis selesai: {total_divisions} divisi, "
                f"verifikasi {verification_rate:.1f}%"
            )

            # Show success message
            self.show_success("Analisis selesai! Laporan akan dibuat otomatis.")

            # Auto-generate reports
            self.root.after(1000, self.auto_generate_reports)

    def on_analysis_error(self, error_message: str):
        """Handle analysis error"""
        self.is_analyzing = False
        self.stop_button.config(state=tk.DISABLED)

        self.progress_widget.set_status("Error")
        self.update_status(f"Analysis gagal: {error_message}")

        self.show_error(f"Analisis gagal: {error_message}")

    def auto_generate_reports(self):
        """Auto-generate reports after successful analysis"""
        if not self.current_analysis:
            return

        try:
            # Generate reports
            generated_files = self.report_service.generate_multi_format_reports(
                self.current_analysis
            )

            # Display results
            file_count = len(generated_files)
            self.results_widget.display_report_files(generated_files)

            self.update_status(f"{file_count} laporan berhasil dibuat")

            # Show notification
            file_list = '\n'.join([
                f"• {file_type}: {os.path.basename(filepath)}"
                for file_type, filepath in generated_files.items()
            ])

            self.show_info(
                f"Berhasil membuat {file_count} laporan:\n\n{file_list}\n\n"
                "Laporan tersimpan di folder 'reports' dalam direktori aplikasi."
            )

        except Exception as e:
            self.show_error(f"Gagal membuat laporan: {e}")

    def validate_all_estates(self):
        """Validate all estate configurations"""
        try:
            self.update_status("Memvalidasi semua estate...")
            validation_results = self.config_service.validate_all_estates()

            total = len(validation_results)
            valid = sum(1 for result in validation_results.values()
                         if result.get('has_fdb', False) and result.get('readable', False))

            if total == valid:
                self.update_status(f"Semua {total} estate valid")
                self.show_info(f"Semua {total} estate valid dan siap digunakan.")
            else:
                invalid = total - valid
                self.update_status(f"{valid}/{total} estate valid, {invalid} bermasalah")
                self.show_warning(
                    f"Hasil validasi:\n"
                    f"• {valid} estate valid\n"
                    f"• {invalid} estate tidak valid\n\n"
                    f"Silakan periksa konfigurasi estate untuk memperbaiki masalah."
                )

        except Exception as e:
            self.show_error(f"Error validasi estate: {e}")

    def test_connections(self):
        """Test connections for all estates"""
        try:
            self.update_status("Menguji koneksi semua estate...")
            self.estate_widget.test_connections()

        except Exception as e:
            self.show_error(f"Error testing connections: {e}")

    def clear_results(self):
        """Clear current results"""
        self.results_widget.clear_results()
        self.progress_widget.reset()
        self.current_analysis = None
        self.update_status("Hasil dibersihkan")

    def open_reports_folder(self):
        """Open reports folder"""
        try:
            reports_dir = "reports"
            if os.path.exists(reports_dir):
                os.startfile(reports_dir)
            else:
                self.show_info(f"Folder reports tidak ditemukan di: {os.path.abspath(reports_dir)}")

        except Exception as e:
            self.show_error(f"Error membuka folder reports: {e}")

    def export_analysis(self):
        """Export current analysis results"""
        if not self.current_analysis:
            self.show_warning("Tidak ada hasil analisis untuk diekspor.")
            return

        try:
            # Export to Excel
            from infrastructure.reporting.excel_exporter import ExcelExporter
            exporter = ExcelExporter()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_file = f"analysis_export_{timestamp}.xlsx"

            excel_path = exporter.create_detailed_report(
                self.current_analysis,
                excel_file
            )

            self.show_info(f"Analisis diekspor ke: {excel_path}")

        except Exception as e:
            self.show_error(f"Error ekspor analisis: {e}")

    def backup_configuration(self):
        """Backup current configuration"""
        try:
            backup_path = self.config_service.backup_configuration()
            self.show_info(f"Konfigurasi dibackup ke: {backup_path}")

        except Exception as e:
            self.show_error(f"Error backup konfigurasi: {e}")

    def clear_reports(self):
        """Clear old report files"""
        try:
            deleted_count = self.report_service.cleanup_old_reports(days_to_keep=7)
            if deleted_count > 0:
                self.show_info(f"{deleted_count} file lama dihapus.")
            else:
                self.show_info("Tidak ada file lama untuk dihapus.")

        except Exception as e:
            self.show_error(f"Error menghapus file lama: {e}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        FFB SCANNER ANALYSIS SYSTEM
        Version 2.0 (Refactored)

        Sistem monitoring data quality transaksi FFB (Fresh Fruit Bunch)
        untuk operasional perkebunan kelapa sawit multi-estate.

        Fitur Utama:
        • Analisis multi-estate hingga 10 estate
        • Monitoring kinerja Kerani, Mandor, dan Asisten
        • Deteksi perbedaan input data
        • Generate laporan PDF dan Excel profesional
        • Validasi koneksi database otomatis
        • Arsitektur modular dan maintainable

        Dikembangkan dengan:
        • Python 3.x + Tkinter
        • ReportLab (PDF Generation)
        • Pandas (Data Processing)
        • Firebird Database Integration

        © 2025 PT. Rebinmas Jaya
        Version: 2.0
        """

        messagebox.showinfo("Tentang Aplikasi", about_text)

    def show_help(self):
        """Show help dialog"""
        self.notebook.select(3)  # Switch to Help tab

    def on_estate_selection_changed(self):
        """Handle estate selection change"""
        # Update connection status
        selected_count = self.estate_widget.get_selected_count()
        valid_count = self.estate_widget.get_valid_selected_count()

        self.connection_status.config(text=f"{valid_count}/{selected_count} connected")

        # Enable/disable analysis button based on selection
        analysis_buttons = [
            self.estate_widget.winfo_children()[6],  # Mulai Analisis Estate button
            self.estate_widget.winfo_children()[7],  # Analisis Terpilih button
        ]

        has_valid_selection = valid_count > 0
        for button in analysis_buttons:
            if hasattr(button, 'winfo_name'):
                button_name = button.winfo_name()
                if button_name.endswith('button'):
                    button.config(state=tk.NORMAL if has_valid_selection else tk.DISABLED)

    def on_date_range_changed(self):
        """Handle date range change"""
        # Update date validation
        self.date_widget.validate_date_range()

    def update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)

    def show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)

    def show_warning(self, message: str):
        """Show warning message"""
        messagebox.showwarning("Peringatan", message)

    def show_info(self, message: str):
        """Show info message"""
        messagebox.showinfo("Informasi", message)

    def show_success(self, message: str):
        """Show success message"""
        messagebox.showinfo("Sukses", message)

    def on_closing(self):
        """Handle window closing"""
        try:
            # Check if analysis is running
            if self.is_analyzing:
                result = messagebox.askyesno(
                    "Analisis Berjalan",
                    "Analisis sedang berjalan. Apakah Anda yakin ingin keluar?"
                )
                if not result:
                    return

            # Cleanup and close
            self.cleanup()
            self.root.destroy()

        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.root.destroy()

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Clear current analysis
            self.current_analysis = None
            self.is_analyzing = False

            # Clear caches
            if self.config_service:
                self.config_service.clear_cache()

        except Exception as e:
            print(f"Cleanup error: {e}")