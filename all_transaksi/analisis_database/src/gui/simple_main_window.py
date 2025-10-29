"""
Simple Main Window - Minimalist GUI untuk FFB Analysis
Hanya: Pilih Estate, Pilih Tanggal, Start Laporan, Ubah Database Path
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple

from services.simple_configuration_service import SimpleConfigurationService
from services.validation_service import ValidationService
from services.analysis_service import AnalysisService
from services.report_generation_service import ReportGenerationService
from services.employee_performance_service import EmployeePerformanceService


class SimpleMainWindow:
    """
    Simple main window - hanya fitur esensial
    """

    def __init__(self, root: tk.Tk,
                 config_service: SimpleConfigurationService,
                 validation_service: ValidationService,
                 analysis_service: AnalysisService,
                 report_service: ReportGenerationService,
                 performance_service: EmployeePerformanceService):
        """
        Initialize simple main window

        :param root: Tkinter root window
        :param config_service: Simple configuration service
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
        self.is_analyzing = False

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup simple UI"""
        # Configure root window
        self.root.title("FFB Scanner Analysis System - Simple")
        self.root.geometry("500x600")
        self.root.configure(bg='#f0f0f0')

        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_container,
            text="SISTEM ANALISIS FFB SCANNER",
            font=('Arial', 14, 'bold'),
            foreground='#2E4057'
        )
        title_label.pack(pady=(0, 20))

        # 1. Estate Selection Section
        self.create_estate_section(main_container)

        # 2. Date Selection Section
        self.create_date_section(main_container)

        # 3. Database Path Section
        self.create_database_section(main_container)

        # 4. Start Report Button
        self.create_start_button(main_container)

        # 5. Status Section
        self.create_status_section(main_container)

    def create_estate_section(self, parent):
        """Create estate selection section"""
        # Frame
        estate_frame = ttk.LabelFrame(parent, text="1. Pilih Estate", padding="10")
        estate_frame.pack(fill=tk.X, pady=(0, 10))

        # Scrollable frame untuk checkboxes
        canvas = tk.Canvas(estate_frame, height=120)
        scrollbar = ttk.Scrollbar(estate_frame, orient="vertical", command=canvas.yview)
        self.estate_checkboxes_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.create_window((0, 0), window=self.estate_checkboxes_frame, anchor="nw")
        self.estate_checkboxes_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Load estates
        self.load_estates()

    def load_estates(self):
        """Load estate configurations"""
        try:
            # Clear existing checkboxes
            for widget in self.estate_checkboxes_frame.winfo_children():
                widget.destroy()

            # Get configurations
            estate_configs = self.config_service.get_estate_configurations()

            if not estate_configs:
                ttk.Label(self.estate_checkboxes_frame, text="Tidak ada estate yang dikonfigurasi",
                         foreground="red").pack()
                return

            # Create checkboxes
            self.estate_vars = {}
            self.estate_paths = {}

            for estate_name, db_path in estate_configs.items():
                # Check jika file exists
                file_exists = self.config_service.validate_estate_path(db_path)
                status_text = "✓" if file_exists else "✗"
                status_color = "green" if file_exists else "red"

                # Frame
                estate_frame = ttk.Frame(self.estate_checkboxes_frame)
                estate_frame.pack(fill=tk.X, pady=1, anchor="w")

                # Checkbox
                var = tk.BooleanVar()
                self.estate_vars[estate_name] = var
                self.estate_paths[estate_name] = db_path

                checkbox = ttk.Checkbutton(
                    estate_frame,
                    text=f"{estate_name}",
                    variable=var,
                    command=self.update_status
                )
                checkbox.pack(side=tk.LEFT)

                # Status
                status_label = ttk.Label(
                    estate_frame,
                    text=f"  ({status_text})",
                    foreground=status_color,
                    font=('Arial', 8)
                )
                status_label.pack(side=tk.LEFT, padx=(5, 0))

            # Select all button
            ttk.Button(
                self.estate_checkboxes_frame,
                text="Pilih Semua",
                command=self.select_all_estates
            ).pack(pady=(5, 0))

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat estate: {e}")

    def select_all_estates(self):
        """Select all estates"""
        for var in self.estate_vars.values():
            var.set(True)
        self.update_status()

    def create_date_section(self, parent):
        """Create date selection section"""
        date_frame = ttk.LabelFrame(parent, text="2. Pilih Tanggal", padding="10")
        date_frame.pack(fill=tk.X, pady=(0, 10))

        # From date
        ttk.Label(date_frame, text="Dari:").grid(row=0, column=0, sticky="w", pady=2)
        self.from_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=15)
        self.from_date_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)

        # To date
        ttk.Label(date_frame, text="Sampai:").grid(row=1, column=0, sticky="w", pady=2)
        self.to_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=15)
        self.to_date_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)

        # Date picker buttons
        ttk.Button(
            date_frame,
            text="Pilih Tanggal Dari",
            command=lambda: self.pick_date(self.from_date_var)
        ).grid(row=0, column=2, padx=(10, 0), pady=2)

        ttk.Button(
            date_frame,
            text="Pilih Tanggal Sampai",
            command=lambda: self.pick_date(self.to_date_var)
        ).grid(row=1, column=2, padx=(10, 0), pady=2)

    def pick_date(self, date_var):
        """Pick date using calendar"""
        try:
            from tkcalendar import DateDialog
            dialog = DateDialog(self.root, date_var.get())
            if dialog.result:
                date_var.set(dialog.result.strftime("%Y-%m-%d"))
        except ImportError:
            # Fallback: input dialog
            from tkinter.simpledialog import askstring
            date_str = askstring("Tanggal", "Masukkan tanggal (YYYY-MM-DD):", initialvalue=date_var.get())
            if date_str:
                date_var.set(date_str)

    def create_database_section(self, parent):
        """Create database path section"""
        db_frame = ttk.LabelFrame(parent, text="3. Database Path", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 10))

        # Current config display
        ttk.Label(db_frame, text="File Konfigurasi:").pack(anchor="w")
        self.config_label = ttk.Label(
            db_frame,
            text=self.config_service.config_file_path,
            font=('Arial', 8),
            foreground="blue"
        )
        self.config_label.pack(anchor="w", pady=(0, 5))

        # Buttons
        button_frame = ttk.Frame(db_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="Buka Config File",
            command=self.open_config_file
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Edit Database Path",
            command=self.edit_database_paths
        ).pack(side=tk.LEFT)

    def open_config_file(self):
        """Open configuration file"""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(self.config_service.config_file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.config_service.config_file_path])
            else:  # Linux
                subprocess.run(["xdg-open", self.config_service.config_file_path])

            messagebox.showinfo("Info", f"Config file dibuka:\n{self.config_service.config_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka config file: {e}")

    def edit_database_paths(self):
        """Edit database paths dialog"""
        dialog = DatabasePathDialog(self.root, self.config_service)
        if dialog.result:
            # Refresh estate display
            self.load_estates()
            messagebox.showinfo("Sukses", "Database paths berhasil diperbarui")

    def create_start_button(self, parent):
        """Create start report button"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="🚀 START LAPORAN",
            command=self.start_analysis,
            style="Accent.TButton"
        )
        self.start_button.pack(fill=tk.X, ipady=10)

    def create_status_section(self, parent):
        """Create status section"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            status_frame,
            text="Siap untuk analisis",
            foreground="green"
        )
        self.status_label.pack()

    def update_status(self):
        """Update status"""
        try:
            selected_count = sum(var.get() for var in self.estate_vars.values())
            valid_selected = 0

            for estate_name, var in self.estate_vars.items():
                if var.get():
                    db_path = self.estate_paths[estate_name]
                    if self.config_service.validate_estate_path(db_path):
                        valid_selected += 1

            if selected_count == 0:
                self.status_label.config(text="Belum ada estate yang dipilih", foreground="orange")
            elif valid_selected == 0:
                self.status_label.config(text="Tidak ada database file yang valid", foreground="red")
            elif valid_selected < selected_count:
                self.status_label.config(text=f"{valid_selected}/{selected_count} estate valid", foreground="orange")
            else:
                self.status_label.config(text=f"{selected_count} estate siap untuk analisis", foreground="green")

        except Exception as e:
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def start_analysis(self):
        """Start analysis and generate report"""
        try:
            if self.is_analyzing:
                messagebox.showwarning("Peringatan", "Analisis sedang berjalan...")
                return

            # Get selected estates
            selected_configs = []
            for estate_name, var in self.estate_vars.items():
                if var.get():
                    db_path = self.estate_paths[estate_name]
                    if self.config_service.validate_estate_path(db_path):
                        selected_configs.append((estate_name, db_path))

            if not selected_configs:
                messagebox.showerror("Error", "Silakan pilih minimal satu estate dengan database file yang valid")
                return

            # Get dates
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()

            if not from_date or not to_date:
                messagebox.showerror("Error", "Silakan pilih tanggal mulai dan tanggal akhir")
                return

            # Validate dates
            try:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Error", "Format tanggal tidak valid. Gunakan format YYYY-MM-DD")
                return

            if from_date_obj > to_date_obj:
                messagebox.showerror("Error", "Tanggal mulai tidak boleh lebih besar dari tanggal akhir")
                return

            # Start analysis
            self.is_analyzing = True
            self.start_button.config(state="disabled", text="⏳ Sedang Menganalisis...")
            self.status_label.config(text="Memulai analisis...", foreground="blue")

            # Run analysis in background
            import threading
            analysis_thread = threading.Thread(
                target=self.run_analysis,
                args=(selected_configs, from_date_obj, to_date_obj),
                daemon=True
            )
            analysis_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai analisis: {e}")
            self.reset_analysis_state()

    def run_analysis(self, selected_configs, from_date, to_date):
        """Run analysis in background thread"""
        try:
            # Run analysis
            analysis_result = self.analysis_service.analyze_multiple_estates(
                estate_configs=selected_configs,
                start_date=from_date,
                end_date=to_date
            )

            # Update UI in main thread
            self.root.after(0, lambda: self.on_analysis_complete(analysis_result))

        except Exception as e:
            self.root.after(0, lambda: self.on_analysis_error(str(e)))

    def on_analysis_complete(self, analysis_result):
        """Handle analysis completion"""
        try:
            self.is_analyzing = False
            self.start_button.config(state="normal", text="🚀 START LAPORAN")
            self.status_label.config(text="Analisis selesai, membuat laporan...", foreground="green")

            # Generate reports
            generated_files = self.report_service.generate_multi_format_reports(analysis_result)

            # Show results
            file_list = "\n".join([f"• {file_type}: {filepath}"
                                  for file_type, filepath in generated_files.items()])

            messagebox.showinfo(
                "Laporan Berhasil Dibuat!",
                f"Analisis selesai!\n\nLaporan yang dibuat:\n{file_list}\n\nFile tersimpan di folder 'reports/'"
            )

            self.status_label.config(text="Laporan berhasil dibuat!", foreground="green")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat laporan: {e}")
            self.reset_analysis_state()

    def on_analysis_error(self, error_message):
        """Handle analysis error"""
        self.is_analyzing = False
        self.start_button.config(state="normal", text="🚀 START LAPORAN")
        self.status_label.config(text=f"Error: {error_message}", foreground="red")
        messagebox.showerror("Error", f"Analisis gagal: {error_message}")

    def reset_analysis_state(self):
        """Reset analysis state"""
        self.is_analyzing = False
        self.start_button.config(state="normal", text="🚀 START LAPORAN")
        self.update_status()


class DatabasePathDialog:
    """Dialog untuk edit database paths"""

    def __init__(self, parent, config_service: SimpleConfigurationService):
        self.parent = parent
        self.config_service = config_service
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Database Paths")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.center_dialog()

    def setup_ui(self):
        """Setup dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Edit Database Paths",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 10))

        # Scrollable frame untuk estate paths
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.paths_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.create_window((0, 0), window=self.paths_frame, anchor="nw")
        self.paths_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Load current paths
        self.load_paths()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="Simpan",
            command=self.save_paths
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Batal",
            command=self.cancel
        ).pack(side=tk.LEFT)

    def load_paths(self):
        """Load current estate paths"""
        try:
            self.path_vars = {}
            configs = self.config_service.get_estate_configurations()

            for i, (estate_name, db_path) in enumerate(configs.items()):
                # Estate name
                ttk.Label(
                    self.paths_frame,
                    text=f"Estate {estate_name}:"
                ).grid(row=i, column=0, sticky="w", pady=2, padx=(0, 10))

                # Path entry
                var = tk.StringVar(value=db_path)
                self.path_vars[estate_name] = var

                entry = ttk.Entry(self.paths_frame, textvariable=var, width=50)
                entry.grid(row=i, column=1, sticky="ew", pady=2)

                # Browse button
                ttk.Button(
                    self.paths_frame,
                    text="Browse",
                    command=lambda en=entry: self.browse_file(en)
                ).grid(row=i, column=2, padx=(5, 0), pady=2)

            # Configure grid weights
            self.paths_frame.columnconfigure(1, weight=1)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat paths: {e}")

    def browse_file(self, entry):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            title="Pilih File Database (.FDB)",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def save_paths(self):
        """Save updated paths"""
        try:
            updated_configs = {}
            for estate_name, var in self.path_vars.items():
                path = var.get().strip()
                if path:
                    updated_configs[estate_name] = path

            # Save to configuration
            self.config_service.estate_configs = updated_configs
            if self.config_service._save_configurations():
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Gagal menyimpan konfigurasi")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")

    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()

    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")