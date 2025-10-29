"""
Main Report Window
Main GUI window for the modular report generation system
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import threading
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from presentation.widgets.month_selection_widget import MonthSelectionWidget
from presentation.widgets.estate_multiselect_widget import EstateMultiSelectWidget
from presentation.widgets.template_selection_widget import TemplateSelectionWidget
from presentation.widgets.progress_indicator_widget import ProgressIndicatorWidget
from presentation.widgets.export_options_widget import ExportOptionsWidget
from presentation.widgets.automated_report_widget import AutomatedReportWidget

from business.services.template_service import TemplateService
from business.services.report_generation_service import ReportGenerationService
from business.services.validation_service import ValidationService
from business.services.automated_report_service import AutomatedReportService
from business.models.report_request import ReportRequest
from infrastructure.exceptions.custom_exceptions import *


class MainReportWindow:
    """
    Main window for modular report generation system
    """
    
    def __init__(self, root: tk.Tk, config_path=None):
        """
        Initialize main report window
        
        Args:
            root: Tkinter root window
            config_path: Optional configuration file path
        """
        self.root = root
        self.config_path = config_path
        
        # Initialize services
        self.template_service = TemplateService()
        self.report_service = ReportGenerationService()
        self.validation_service = ValidationService()
        self.automated_service = AutomatedReportService(self.report_service, self.validation_service)
        
        self.logger = logging.getLogger(__name__)
        
        # Application state
        self.current_request: Optional[ReportRequest] = None
        self.is_generating = False
        self.generation_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_report_complete: Optional[Callable] = None
        self.on_report_error: Optional[Callable] = None
        
        # Setup UI
        self.setup_window()
        self.setup_ui()
        self.setup_bindings()
        
        # Initialize widgets after UI is set up
        self.initialize_widgets()
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Cancel any running report generation
            if hasattr(self, 'current_report_thread') and self.current_report_thread:
                self.report_service.cancel_report()
                
            # Save any pending configurations
            self.save_window_state()
            
            self.logger.info("Application closing gracefully")
            
        except Exception as e:
            self.logger.error(f"Error during application closing: {e}")
        finally:
            self.root.destroy()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Sistem Generasi Laporan Modular - FFB Scanner")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)
        
        # Center window on screen
        self.center_window()
        
        # Set minimum size
        self.root.minsize(800, 600)
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.create_title()
        
        # Create notebook for tabs
        self.create_notebook()
        
        # Create main tab
        self.create_main_tab()
        
        # Create automated report tab
        self.create_automated_tab()
        
    def create_automated_tab(self):
        """Create automated report generation tab"""
        self.automated_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.automated_tab, text="Laporan Otomatis")
        
        # Create automated report widget
        self.automated_widget = AutomatedReportWidget(
            self.automated_tab,
            self.automated_service
        )
        
        # Pack the widget's main frame
        self.automated_widget.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create settings tab
        self.create_settings_tab()
        
        # Create help tab
        self.create_help_tab()
        
        # Status bar
        self.create_status_bar()
        
        # Menu bar
        self.create_menu_bar()
    
    def create_title(self):
        """Create title section"""
        title_frame = ttk.Frame(self.main_container)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="SISTEM GENERASI LAPORAN MODULAR",
            font=('Arial', 18, 'bold'),
            foreground='#2E4057'
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="FFB Scanner Multi-Estate Report Generator",
            font=('Arial', 12),
            foreground='#666666'
        )
        subtitle_label.pack()
    
    def create_notebook(self):
        """Create notebook for tabs"""
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    def create_main_tab(self):
        """Create main report generation tab"""
        # Main tab frame
        self.main_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.main_tab, text="Generasi Laporan")
        
        # Create sections
        self.create_selection_section()
        self.create_options_section()
        self.create_action_section()
        self.create_progress_section()
    
    def create_selection_section(self):
        """Create selection section"""
        selection_frame = ttk.LabelFrame(
            self.main_tab,
            text="Pilihan Parameter Laporan",
            padding="15"
        )
        selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create grid layout
        selection_frame.columnconfigure(1, weight=1)
        
        # Month selection
        month_label = ttk.Label(selection_frame, text="Bulan:")
        month_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        self.month_widget = MonthSelectionWidget(selection_frame)
        self.month_widget.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Estate selection
        estate_label = ttk.Label(selection_frame, text="Estate:")
        estate_label.grid(row=1, column=0, sticky=tk.W+tk.N, padx=(0, 10), pady=5)
        
        self.estate_widget = EstateMultiSelectWidget(selection_frame)
        self.estate_widget.grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        
        # Template selection
        template_label = ttk.Label(selection_frame, text="Template:")
        template_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        self.template_widget = TemplateSelectionWidget(selection_frame, self.template_service)
        self.template_widget.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Configure row weights
        selection_frame.rowconfigure(1, weight=1)
    
    def create_options_section(self):
        """Create options section"""
        options_frame = ttk.LabelFrame(
            self.main_tab,
            text="Opsi Export",
            padding="15"
        )
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.export_widget = ExportOptionsWidget(options_frame)
        self.export_widget.pack(fill=tk.X)
    
    def create_action_section(self):
        """Create action buttons section with prominent Start Generate button"""
        action_frame = ttk.Frame(self.main_tab)
        action_frame.pack(fill=tk.X, pady=(20, 15))
        
        # Create prominent start button section
        start_section = ttk.Frame(action_frame)
        start_section.pack(fill=tk.X, pady=(0, 20))
        
        # Workflow guidance label
        guidance_label = ttk.Label(
            start_section,
            text="🔄 Alur Kerja: Pilih Bulan → Pilih Estate → Pilih Template → Klik Tombol di Bawah",
            font=('Arial', 11, 'bold'),
            foreground='#2E4057',
            background='#E8F4FD',
            padding=(10, 8)
        )
        guidance_label.pack(fill=tk.X, pady=(0, 15))
        
        # Prominent Start Generate button
        self.start_generate_button = tk.Button(
            start_section,
            text="🚀 START GENERATE LAPORAN",
            command=self.start_report_generation_workflow,
            font=('Arial', 16, 'bold'),
            bg='#28A745',  # Green background
            fg='white',    # White text
            activebackground='#218838',  # Darker green when pressed
            activeforeground='white',
            relief='raised',
            bd=3,
            padx=40,
            pady=20,
            cursor='hand2'
        )
        self.start_generate_button.pack(pady=(0, 10))
        
        # Status indicator for the prominent button
        self.workflow_status_label = ttk.Label(
            start_section,
            text="✅ Siap untuk memulai generasi laporan",
            font=('Arial', 10),
            foreground='#28A745'
        )
        self.workflow_status_label.pack()
        
        # Separator
        separator = ttk.Separator(action_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 15))
        
        # Secondary action buttons frame
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(anchor=tk.CENTER)
        
        # Traditional Generate button (smaller, secondary)
        self.generate_button = ttk.Button(
            button_frame,
            text="Generate Laporan",
            command=self.start_report_generation,
            style="Accent.TButton",
            state=tk.DISABLED  # Disabled by default, use prominent button instead
        )
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Batal",
            command=self.cancel_report_generation,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self.clear_selections
        )
        self.clear_button.pack(side=tk.LEFT)
    
    def create_progress_section(self):
        """Create progress section"""
        progress_frame = ttk.LabelFrame(
            self.main_tab,
            text="Progress",
            padding="15"
        )
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        self.progress_widget = ProgressIndicatorWidget(progress_frame)
        self.progress_widget.pack(fill=tk.BOTH, expand=True)
    
    def create_settings_tab(self):
        """Create settings tab"""
        self.settings_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.settings_tab, text="Pengaturan")
        
        # Template management section
        template_mgmt_frame = ttk.LabelFrame(
            self.settings_tab,
            text="Manajemen Template",
            padding="15"
        )
        template_mgmt_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Refresh templates button
        refresh_button = ttk.Button(
            template_mgmt_frame,
            text="Refresh Template",
            command=self.refresh_templates
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Template directory button
        template_dir_button = ttk.Button(
            template_mgmt_frame,
            text="Buka Direktori Template",
            command=self.open_template_directory
        )
        template_dir_button.pack(side=tk.LEFT)
        
        # Estate configuration section
        estate_config_frame = ttk.LabelFrame(
            self.settings_tab,
            text="Konfigurasi Estate",
            padding="15"
        )
        estate_config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Configure estates button
        config_estates_button = ttk.Button(
            estate_config_frame,
            text="Konfigurasi Estate",
            command=self.configure_estates
        )
        config_estates_button.pack(side=tk.LEFT)
    
    def create_help_tab(self):
        """Create help tab"""
        self.help_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.help_tab, text="Bantuan")
        
        # Help text
        help_text = tk.Text(
            self.help_tab,
            wrap=tk.WORD,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Add help content
        help_content = self.get_help_content()
        help_text.config(state=tk.NORMAL)
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.main_container)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(
            self.status_bar,
            text="Siap",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Version label
        version_label = ttk.Label(
            self.status_bar,
            text="v1.0.0",
            relief=tk.SUNKEN
        )
        version_label.pack(side=tk.RIGHT)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Baru", command=self.new_report)
        file_menu.add_separator()
        file_menu.add_command(label="Buka Folder Laporan", command=self.open_reports_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh Template", command=self.refresh_templates)
        tools_menu.add_command(label="Validasi Konfigurasi", command=self.validate_configuration)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bantuan", menu=help_menu)
        help_menu.add_command(label="Panduan Penggunaan", command=self.show_user_guide)
        help_menu.add_separator()
        help_menu.add_command(label="Tentang", command=self.show_about)
    
    def setup_bindings(self):
        """Setup event bindings"""
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Widget change events
        self.month_widget.on_change = self.on_selection_changed
        self.estate_widget.on_change = self.on_selection_changed
        self.template_widget.on_change = self.on_selection_changed
    
    def save_window_state(self):
        """Save window state and user preferences"""
        try:
            # This could save window size, position, last selected options, etc.
            # For now, just log that we're saving state
            self.logger.info("Saving window state and user preferences")
            
        except Exception as e:
            self.logger.error(f"Error saving window state: {e}")
    
    def load_initial_data(self):
        """Load initial data for the application"""
        try:
            # Load templates
            self.template_widget.refresh_templates()
            
            # Load estates from config if provided
            if self.config_path:
                self.estate_widget.load_estates_from_config(self.config_path)
            
            self.logger.info("Initial data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
            messagebox.showerror("Error", f"Failed to load initial data: {str(e)}")
    
    def initialize_widgets(self):
        """Initialize widgets with data"""
        try:
            # Initialize estate widget
            self.estate_widget.load_estates()
            
            # Initialize template widget
            self.template_widget.refresh_templates()
            
            # Set default month to current month
            self.month_widget.set_current_month()
            
            self.update_status("Sistem siap digunakan")
            
            self.logger.info("All widgets initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing widgets: {e}")
            self.show_error(f"Error saat inisialisasi: {e}")
            raise
    
    def start_report_generation_workflow(self):
        """Enhanced workflow for report generation with step-by-step validation"""
        try:
            # Step 1: Validate month selection
            if not self.month_widget.get_selected_month():
                self.workflow_status_label.config(
                    text="❌ Pilih bulan terlebih dahulu!",
                    foreground='#DC3545'
                )
                self.show_warning("Silakan pilih bulan untuk laporan terlebih dahulu.")
                return
            
            # Step 2: Validate estate selection
            selected_estates = self.estate_widget.get_selected_estates()
            if not selected_estates:
                self.workflow_status_label.config(
                    text="❌ Pilih minimal satu estate!",
                    foreground='#DC3545'
                )
                self.show_warning("Silakan pilih minimal satu estate untuk laporan.")
                return
            
            # Step 3: Validate template selection
            selected_template = self.template_widget.get_selected_template()
            if not selected_template:
                self.workflow_status_label.config(
                    text="❌ Pilih template laporan!",
                    foreground='#DC3545'
                )
                self.show_warning("Silakan pilih template laporan yang diinginkan.")
                return
            
            # Step 4: Show confirmation dialog with summary
            month_name = self.month_widget.get_selected_month_name()
            estate_names = [estate['name'] for estate in selected_estates]
            template_name = selected_template.get('name', 'Unknown Template')
            
            confirmation_message = f"""
Konfirmasi Generasi Laporan:

📅 Bulan: {month_name}
🏢 Estate: {', '.join(estate_names)}
📋 Template: {template_name}

Apakah Anda yakin ingin melanjutkan?
            """
            
            if not messagebox.askyesno("Konfirmasi Generasi Laporan", confirmation_message):
                self.workflow_status_label.config(
                    text="⏸️ Generasi laporan dibatalkan",
                    foreground='#FFC107'
                )
                return
            
            # Step 5: Update status and start generation
            self.workflow_status_label.config(
                text="🚀 Memulai generasi laporan...",
                foreground='#007BFF'
            )
            
            # Disable the prominent button during generation
            self.start_generate_button.config(state=tk.DISABLED)
            
            # Call the original report generation method
            self.start_report_generation()
            
        except Exception as e:
            self.logger.error(f"Error in workflow: {e}")
            self.workflow_status_label.config(
                text="❌ Error dalam alur kerja",
                foreground='#DC3545'
            )
            self.show_error(f"Error dalam alur kerja: {e}")

    def start_report_generation(self):
        """Start report generation process"""
        try:
            # Validate selections
            if not self.validate_selections():
                return
            
            # Create report request
            request = self.create_report_request()
            if not request:
                return
            
            # Update UI state
            self.set_generating_state(True)
            
            # Start generation in background thread
            self.generation_thread = threading.Thread(
                target=self.generate_report_thread,
                args=(request,),
                daemon=True
            )
            self.generation_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting report generation: {e}")
            self.show_error(f"Error memulai generasi laporan: {e}")
            self.set_generating_state(False)
    
    def generate_report_thread(self, request: ReportRequest):
        """Generate report in background thread"""
        try:
            # Update progress
            self.progress_widget.start_progress("Memulai generasi laporan...")
            
            # Generate report
            result = self.report_service.generate_report(
                request,
                progress_callback=self.progress_widget.update_progress
            )
            
            # Report generation completed
            self.root.after(0, self.on_report_generation_complete, result)
            
        except Exception as e:
            self.logger.error(f"Error in report generation thread: {e}")
            self.root.after(0, self.on_report_generation_error, str(e))
    
    def cancel_report_generation(self):
        """Cancel report generation"""
        try:
            if self.is_generating and self.report_service:
                self.report_service.cancel_generation()
                self.progress_widget.cancel_progress()
                self.set_generating_state(False)
                self.update_status("Generasi laporan dibatalkan")
                
        except Exception as e:
            self.logger.error(f"Error canceling report generation: {e}")
    
    def on_report_generation_complete(self, result):
        """Handle report generation completion"""
        try:
            self.set_generating_state(False)
            self.progress_widget.complete_progress("Laporan berhasil dibuat!")
            
            # Show success message
            message = f"Laporan berhasil dibuat!\n\nFile: {result.output_path}"
            messagebox.showinfo("Sukses", message)
            
            # Update status
            self.update_status("Laporan berhasil dibuat")
            
            # Call completion callback if set
            if self.on_report_complete:
                self.on_report_complete(result)
                
        except Exception as e:
            self.logger.error(f"Error handling report completion: {e}")
    
    def on_report_generation_error(self, error_message: str):
        """Handle report generation error"""
        try:
            self.set_generating_state(False)
            self.progress_widget.error_progress(f"Error: {error_message}")
            
            # Show error message
            self.show_error(f"Error saat generasi laporan:\n{error_message}")
            
            # Update status
            self.update_status("Error generasi laporan")
            
            # Call error callback if set
            if self.on_report_error:
                self.on_report_error(error_message)
                
        except Exception as e:
            self.logger.error(f"Error handling report error: {e}")
    
    def validate_selections(self) -> bool:
        """Validate user selections"""
        try:
            # Validate month selection
            if not self.month_widget.get_selected_month():
                self.show_warning("Silakan pilih bulan")
                return False
            
            # Validate estate selection
            selected_estates = self.estate_widget.get_selected_estates()
            if not selected_estates:
                self.show_warning("Silakan pilih minimal satu estate")
                return False
            
            # Validate template selection
            if not self.template_widget.get_selected_template():
                self.show_warning("Silakan pilih template laporan")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating selections: {e}")
            self.show_error(f"Error validasi: {e}")
            return False
    
    def create_report_request(self) -> Optional[ReportRequest]:
        """Create report request from user selections"""
        try:
            # Get selections
            month = self.month_widget.get_selected_month()
            estates = self.estate_widget.get_selected_estates()
            template = self.template_widget.get_selected_template()
            export_options = self.export_widget.get_export_options()
            
            # Create request
            request = ReportRequest(
                month=month,
                estates=estates,
                template=template,
                export_format=export_options['format'],
                output_directory=export_options['output_directory'],
                include_charts=export_options.get('include_charts', False),
                include_summary=export_options.get('include_summary', True)
            )
            
            return request
            
        except Exception as e:
            self.logger.error(f"Error creating report request: {e}")
            self.show_error(f"Error membuat request laporan: {e}")
            return None
    
    def set_generating_state(self, generating: bool):
        """Set UI state for report generation"""
        self.is_generating = generating
        
        # Update button states
        self.start_generate_button.config(state=tk.DISABLED if generating else tk.NORMAL)
        self.generate_button.config(state=tk.DISABLED if generating else tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL if generating else tk.DISABLED)
        
        # Update workflow status
        if generating:
            self.workflow_status_label.config(text="🔄 Sedang memproses laporan...")
        else:
            self.workflow_status_label.config(text="✅ Siap untuk memulai")
        
        # Update widget states
        self.month_widget.set_enabled(not generating)
        self.estate_widget.set_enabled(not generating)
        self.template_widget.set_enabled(not generating)
        self.export_widget.set_enabled(not generating)
    
    def clear_selections(self):
        """Clear all selections"""
        try:
            self.month_widget.clear_selection()
            self.estate_widget.clear_selection()
            self.template_widget.clear_selection()
            self.export_widget.reset_options()
            self.progress_widget.reset_progress()
            
            self.update_status("Pilihan direset")
            
        except Exception as e:
            self.logger.error(f"Error clearing selections: {e}")
    
    def on_selection_changed(self):
        """Handle selection change events"""
        # Update generate button state based on selections
        has_valid_selections = (
            self.month_widget.get_selected_month() and
            self.estate_widget.get_selected_estates() and
            self.template_widget.get_selected_template()
        )
        
        if not self.is_generating:
            self.generate_button.config(
                state=tk.NORMAL if has_valid_selections else tk.DISABLED
            )
    
    def refresh_templates(self):
        """Refresh available templates"""
        try:
            self.template_service.reload_templates()
            self.template_widget.refresh_templates()
            self.update_status("Template berhasil direfresh")
            
        except Exception as e:
            self.logger.error(f"Error refreshing templates: {e}")
            self.show_error(f"Error refresh template: {e}")
    
    def open_template_directory(self):
        """Open template directory"""
        try:
            template_dir = self.template_service.template_directory
            if template_dir.exists():
                import os
                os.startfile(str(template_dir))
            else:
                self.show_warning("Direktori template tidak ditemukan")
                
        except Exception as e:
            self.logger.error(f"Error opening template directory: {e}")
            self.show_error(f"Error membuka direktori template: {e}")
    
    def configure_estates(self):
        """Open estate configuration dialog"""
        # This would open a separate dialog for estate configuration
        self.show_info("Fitur konfigurasi estate akan segera tersedia")
    
    def open_reports_folder(self):
        """Open reports folder"""
        try:
            reports_dir = Path("reports")
            if reports_dir.exists():
                import os
                os.startfile(str(reports_dir))
            else:
                self.show_warning("Folder laporan tidak ditemukan")
                
        except Exception as e:
            self.logger.error(f"Error opening reports folder: {e}")
            self.show_error(f"Error membuka folder laporan: {e}")
    
    def validate_configuration(self):
        """Validate system configuration"""
        try:
            # Validate templates
            templates = self.template_service.get_available_templates()
            if not templates:
                self.show_warning("Tidak ada template yang tersedia")
                return
            
            # Validate estates
            estates = self.estate_widget.get_available_estates()
            if not estates:
                self.show_warning("Tidak ada estate yang dikonfigurasi")
                return
            
            self.show_info("Konfigurasi sistem valid")
            
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            self.show_error(f"Error validasi konfigurasi: {e}")
    
    def new_report(self):
        """Start new report"""
        self.clear_selections()
    
    def show_user_guide(self):
        """Show user guide"""
        self.notebook.select(self.help_tab)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Sistem Generasi Laporan Modular
FFB Scanner Multi-Estate Report Generator

Version: 1.0.0
Developed for: PT. Perkebunan Nusantara

Features:
- Template-based report generation
- Multi-estate support
- Multiple export formats
- Progress tracking
- Modular architecture

© 2024 - All rights reserved
        """
        messagebox.showinfo("Tentang", about_text.strip())
    
    def get_help_content(self) -> str:
        """Get help content text"""
        return """
PANDUAN PENGGUNAAN SISTEM GENERASI LAPORAN MODULAR

1. MEMILIH PARAMETER LAPORAN
   - Pilih bulan dalam format YYYY-MM
   - Pilih satu atau lebih estate dari daftar
   - Pilih template laporan yang sesuai

2. MENGATUR OPSI EXPORT
   - Pilih format export (PDF/Excel)
   - Tentukan direktori output
   - Atur opsi tambahan sesuai kebutuhan

3. GENERATE LAPORAN
   - Klik tombol "Generate Laporan"
   - Pantau progress di bagian bawah
   - Tunggu hingga proses selesai

4. MENGELOLA TEMPLATE
   - Gunakan tab "Pengaturan" untuk mengelola template
   - Refresh template jika ada perubahan
   - Buka direktori template untuk menambah template baru

5. TIPS PENGGUNAAN
   - Pastikan semua parameter telah dipilih sebelum generate
   - Gunakan tombol "Reset" untuk membersihkan pilihan
   - Periksa folder laporan untuk hasil yang telah dibuat

Untuk bantuan lebih lanjut, hubungi administrator sistem.
        """
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def show_warning(self, message: str):
        """Show warning message"""
        messagebox.showwarning("Peringatan", message)
    
    def show_info(self, message: str):
        """Show info message"""
        messagebox.showinfo("Informasi", message)
    
    def on_closing(self):
        """Handle window closing"""
        try:
            # Cancel any running generation
            if self.is_generating:
                self.cancel_report_generation()
            
            # Cleanup
            self.cleanup()
            
            # Close window
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during window closing: {e}")
            self.root.destroy()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel any running threads
            if self.generation_thread and self.generation_thread.is_alive():
                # Note: We can't force kill threads in Python, 
                # but the daemon=True flag will help
                pass
            
            # Clear caches
            if self.template_service:
                self.template_service.clear_cache()
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")