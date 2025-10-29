"""
Report Export Widget
GUI component for exporting reports in various formats with comprehensive options
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path


class ReportExportWidget:
    """
    Widget for comprehensive report export functionality
    """

    def __init__(self, parent_frame, on_generate_report: Optional[Callable] = None):
        """
        Initialize report export widget

        :param parent_frame: Parent tkinter frame
        :param on_generate_report: Optional report generation callback
        """
        self.parent = parent_frame
        self.on_generate_report = on_generate_report

        # Export state
        self.analysis_results = None
        self.export_history = []
        self.default_export_path = self.get_default_export_path()

        # Export settings
        self.export_settings = {
            'include_charts': True,
            'include_detailed_data': False,
            'include_employee_analysis': True,
            'include_summary_only': False,
            'format_date': True,
            'company_name': 'PT. Rebinmas',
            'report_title': 'FFB Scanner Analysis Report'
        }

        self.setup_ui()
        self.load_export_history()

    def setup_ui(self):
        """Setup the report export widget UI"""
        # Main container
        main_container = ttk.LabelFrame(
            self.parent,
            text="Export Laporan",
            padding="15"
        )
        main_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # Report Configuration Section
        config_frame = ttk.LabelFrame(main_container, text="Konfigurasi Laporan", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # Report title
        title_frame = ttk.Frame(config_frame)
        title_frame.pack(fill=tk.X, pady=2)

        ttk.Label(title_frame, text="Judul Laporan:", width=15).pack(side=tk.LEFT)
        self.report_title_var = tk.StringVar(value=self.export_settings['report_title'])
        title_entry = ttk.Entry(title_frame, textvariable=self.report_title_var, width=50)
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Company name
        company_frame = ttk.Frame(config_frame)
        company_frame.pack(fill=tk.X, pady=2)

        ttk.Label(company_frame, text="Nama Perusahaan:", width=15).pack(side=tk.LEFT)
        self.company_name_var = tk.StringVar(value=self.export_settings['company_name'])
        company_entry = ttk.Entry(company_frame, textvariable=self.company_name_var, width=50)
        company_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Report period
        period_frame = ttk.Frame(config_frame)
        period_frame.pack(fill=tk.X, pady=2)

        ttk.Label(period_frame, text="Periode Laporan:", width=15).pack(side=tk.LEFT)
        self.period_var = tk.StringVar(value="Otomatis")
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=["Otomatis", "Hari Ini", "Minggu Ini", "Bulan Ini", "Kustom"],
            state="readonly",
            width=20
        )
        period_combo.pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(period_frame, text="Format Tanggal:", width=12).pack(side=tk.LEFT)
        self.format_date_var = tk.BooleanVar(value=self.export_settings['format_date'])
        format_date_check = ttk.Checkbutton(
            period_frame,
            text="Gunakan format Indonesia",
            variable=self.format_date_var
        )
        format_date_check.pack(side=tk.LEFT)

        # Content Options Section
        content_frame = ttk.LabelFrame(main_container, text="Opsi Konten", padding="10")
        content_frame.pack(fill=tk.X, pady=(0, 10))

        # Content checkboxes
        self.include_charts_var = tk.BooleanVar(value=self.export_settings['include_charts'])
        self.include_detailed_var = tk.BooleanVar(value=self.export_settings['include_detailed_data'])
        self.include_employee_var = tk.BooleanVar(value=self.export_settings['include_employee_analysis'])
        self.include_summary_var = tk.BooleanVar(value=self.export_settings['include_summary_only'])

        content_options = [
            (self.include_charts_var, "Sertakan Grafik dan Visualisasi"),
            (self.include_employee_var, "Sertakan Analisis Performa Karyawan"),
            (self.include_detailed_var, "Sertakan Data Detail Transaksi"),
            (self.include_summary_var, "Ringkasan Saja (tanpa detail)")
        ]

        for i, (var, text) in enumerate(content_options):
            row = i // 2
            col = i % 2

            check = ttk.Checkbutton(content_frame, text=text, variable=var)
            check.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

        # Bind mutually exclusive options
        self.include_summary_var.trace('w', self.on_summary_only_changed)

        # Export Format Section
        format_frame = ttk.LabelFrame(main_container, text="Format Export", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 10))

        # Format selection
        format_select_frame = ttk.Frame(format_frame)
        format_select_frame.pack(fill=tk.X, pady=2)

        ttk.Label(format_select_frame, text="Format:", width=15).pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="PDF")
        formats = [
            ("PDF - Laporan Lengkap", "PDF"),
            ("Excel - Data Analysis", "Excel"),
            ("CSV - Data mentah", "CSV"),
            ("JSON - Data Terstruktur", "JSON"),
            ("Word - Document", "Word"),
            ("PowerPoint - Presentation", "PowerPoint")
        ]

        format_combo = ttk.Combobox(
            format_select_frame,
            textvariable=self.format_var,
            values=[desc for desc, _ in formats],
            state="readonly",
            width=30
        )
        format_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Store format mapping
        self.format_mapping = {desc: fmt for desc, fmt in formats}

        # File location
        location_frame = ttk.Frame(format_frame)
        location_frame.pack(fill=tk.X, pady=(10, 2))

        ttk.Label(location_frame, text="Lokasi File:", width=15).pack(side=tk.LEFT)
        self.export_path_var = tk.StringVar(value=self.default_export_path)
        path_entry = ttk.Entry(location_frame, textvariable=self.export_path_var, width=60)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        ttk.Button(
            location_frame,
            text="Browse...",
            command=self.browse_export_location
        ).pack(side=tk.LEFT)

        # File naming
        naming_frame = ttk.Frame(format_frame)
        naming_frame.pack(fill=tk.X, pady=2)

        ttk.Label(naming_frame, text="Pattern Nama:", width=15).pack(side=tk.LEFT)
        self.filename_pattern_var = tk.StringVar(value="FFB_Analysis_{estate}_{date}")
        pattern_entry = ttk.Entry(naming_frame, textvariable=self.filename_pattern_var, width=40)
        pattern_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(naming_frame, text="Variables: {estate}, {date}, {type}, {timestamp}").pack(side=tk.LEFT)

        # Estate Selection for Export
        estate_frame = ttk.LabelFrame(main_container, text="Pilih Estate untuk Export", padding="10")
        estate_frame.pack(fill=tk.X, pady=(0, 10))

        estate_select_frame = ttk.Frame(estate_frame)
        estate_select_frame.pack(fill=tk.X)

        ttk.Label(estate_select_frame, text="Estate:", width=10).pack(side=tk.LEFT, padx=(0, 10))
        self.export_estate_var = tk.StringVar(value="Semua")
        self.export_estate_combo = ttk.Combobox(
            estate_select_frame,
            textvariable=self.export_estate_var,
            values=["Semua"],
            state="readonly",
            width=30
        )
        self.export_estate_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Estate selection options
        self.export_individual_var = tk.BooleanVar(value=False)
        individual_check = ttk.Checkbutton(
            estate_select_frame,
            text="Export file terpisah per estate",
            variable=self.export_individual_var
        )
        individual_check.pack(side=tk.LEFT)

        # Export Options Section
        options_frame = ttk.LabelFrame(main_container, text="Opsi Export", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Email options
        email_frame = ttk.Frame(options_frame)
        email_frame.pack(fill=tk.X, pady=2)

        self.send_email_var = tk.BooleanVar(value=False)
        email_check = ttk.Checkbutton(
            email_frame,
            text="Kirim via email:",
            variable=self.send_email_var
        )
        email_check.pack(side=tk.LEFT)

        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.email_var, width=40)
        email_entry.pack(side=tk.LEFT, padx=(10, 0))
        email_entry.config(state=tk.DISABLED)

        # Bind email checkbox
        self.send_email_var.trace('w', self.on_email_option_changed)

        # Compression options
        compress_frame = ttk.Frame(options_frame)
        compress_frame.pack(fill=tk.X, pady=2)

        self.compress_var = tk.BooleanVar(value=False)
        compress_check = ttk.Checkbutton(
            compress_frame,
            text="Kompres file (ZIP):",
            variable=self.compress_var
        )
        compress_check.pack(side=tk.LEFT)

        # Action Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Preview button
        ttk.Button(
            button_frame,
            text="Preview Laporan",
            command=self.preview_report
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Generate report button
        self.generate_button = ttk.Button(
            button_frame,
            text="Generate Laporan",
            command=self.generate_report,
            style="Accent.TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=(0, 5))

        # Export template button
        ttk.Button(
            button_frame,
            text="Simpan Template",
            command=self.save_template
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Load Template",
            command=self.load_template
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Progress section
        progress_frame = ttk.LabelFrame(main_container, text="Status Export", padding="10")
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        # Progress bar
        self.export_progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.export_progress.pack(fill=tk.X, pady=(0, 5))

        # Status label
        self.export_status_label = ttk.Label(
            progress_frame,
            text="Siap untuk generate laporan",
            font=('Arial', 9)
        )
        self.export_status_label.pack(anchor=tk.W)

        # Export History Section
        history_frame = ttk.LabelFrame(main_container, text="Riwayat Export", padding="5")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # History treeview
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=("date", "format", "estate", "filename", "status"),
            show="tree headings",
            height=6
        )

        # Configure columns
        self.history_tree.heading("#0", text="ID")
        self.history_tree.heading("date", text="Tanggal")
        self.history_tree.heading("format", text="Format")
        self.history_tree.heading("estate", text="Estate")
        self.history_tree.heading("filename", text="Nama File")
        self.history_tree.heading("status", text="Status")

        # Column widths
        self.history_tree.column("#0", width=40)
        self.history_tree.column("date", width=120)
        self.history_tree.column("format", width=80)
        self.history_tree.column("estate", width=100)
        self.history_tree.column("filename", width=200)
        self.history_tree.column("status", width=80)

        # Scrollbar
        history_scrollbar = ttk.Scrollbar(
            history_frame,
            orient=tk.VERTICAL,
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # History buttons
        history_button_frame = ttk.Frame(history_frame)
        history_button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            history_button_frame,
            text="Buka File",
            command=self.open_exported_file
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            history_button_frame,
            text="Buka Folder",
            command=self.open_export_folder
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            history_button_frame,
            text="Hapus Riwayat",
            command=self.clear_history
        ).pack(side=tk.LEFT)

        # Double-click to open file
        self.history_tree.bind("<Double-1>", lambda e: self.open_exported_file())

    def get_default_export_path(self) -> str:
        """Get default export path"""
        # Try to create reports directory in the project
        project_root = Path(__file__).parent.parent.parent.parent.parent
        reports_dir = project_root / "reports"

        try:
            reports_dir.mkdir(exist_ok=True)
            return str(reports_dir)
        except Exception:
            # Fallback to user documents
            return os.path.join(os.path.expanduser("~"), "Documents", "FFB_Reports")

    def set_analysis_results(self, analysis_results: Dict[str, Any]):
        """
        Set analysis results for export

        :param analysis_results: Analysis results dictionary
        """
        self.analysis_results = analysis_results

        # Update estate options
        if analysis_results:
            estate_results = analysis_results.get('estate_results', {})
            estates = ["Semua"] + list(estate_results.keys())
            self.export_estate_combo['values'] = estates

            # Auto-select first estate if only one
            if len(estates) == 2:
                self.export_estate_var.set(estates[1])

    def on_summary_only_changed(self, *args):
        """Handle summary only option change"""
        if self.include_summary_var.get():
            # Disable other options when summary only is selected
            self.include_charts_var.set(False)
            self.include_detailed_var.set(False)
            self.include_employee_var.set(False)

            # Disable checkboxes
            for widget in self.parent.winfo_children():
                if isinstance(widget, ttk.Checkbutton):
                    widget.config(state=tk.DISABLED)
        else:
            # Re-enable checkboxes
            for widget in self.parent.winfo_children():
                if isinstance(widget, ttk.Checkbutton):
                    widget.config(state=tk.NORMAL)

    def on_email_option_changed(self, *args):
        """Handle email option change"""
        if self.send_email_var.get():
            self.email_entry.config(state=tk.NORMAL)
        else:
            self.email_entry.config(state=tk.DISABLED)
            self.email_var.set("")

    def browse_export_location(self):
        """Browse for export location"""
        folder_path = filedialog.askdirectory(
            title="Pilih Lokasi Export",
            initialdir=self.export_path_var.get()
        )

        if folder_path:
            self.export_path_var.set(folder_path)

    def generate_filename(self) -> str:
        """Generate filename based on pattern"""
        pattern = self.filename_pattern_var.get()
        estate = self.export_estate_var.get()
        format_type = self.format_var.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Format date
        if self.format_date_var.get():
            date_str = datetime.now().strftime("%d_%B_%Y")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # Replace placeholders
        filename = pattern.format(
            estate=estate.lower().replace(" ", "_"),
            date=date_str,
            type=format_type.lower(),
            timestamp=timestamp
        )

        # Add extension
        format_code = self.format_mapping.get(self.format_var.get(), "PDF")
        extensions = {
            "PDF": ".pdf",
            "Excel": ".xlsx",
            "CSV": ".csv",
            "JSON": ".json",
            "Word": ".docx",
            "PowerPoint": ".pptx"
        }

        filename += extensions.get(format_code, ".pdf")

        return filename

    def validate_export_settings(self) -> tuple[bool, str]:
        """
        Validate export settings

        :return: Tuple of (is_valid, error_message)
        """
        # Check if analysis results exist
        if not self.analysis_results:
            return False, "Tidak ada hasil analisis untuk diekspor"

        # Check export path
        export_path = self.export_path_var.get()
        if not export_path or not os.path.exists(export_path):
            return False, "Lokasi export tidak valid atau tidak ada"

        # Check email if enabled
        if self.send_email_var.get():
            email = self.email_var.get().strip()
            if not email:
                return False, "Alamat email harus diisi jika opsi email dipilih"

            # Basic email validation
            if "@" not in email or "." not in email.split("@")[-1]:
                return False, "Format email tidak valid"

        return True, ""

    def generate_report(self):
        """Generate and export report"""
        # Validate settings
        is_valid, error_message = self.validate_export_settings()
        if not is_valid:
            messagebox.showerror("Validasi Error", error_message)
            return

        try:
            # Update UI
            self.generate_button.config(state=tk.DISABLED)
            self.export_progress.config(value=0)
            self.export_status_label.config(text="Memulai generate laporan...")

            # Get export settings
            export_config = self.get_export_config()

            # Generate filename
            filename = self.generate_filename()
            filepath = os.path.join(self.export_path_var.get(), filename)

            # Update progress
            self.export_progress.config(value=20)
            self.export_status_label.config(text="Menggenerate laporan...")

            # Call report generation callback
            if self.on_generate_report:
                success = self.on_generate_report(
                    self.analysis_results,
                    export_config,
                    filepath
                )

                if success:
                    # Update progress
                    self.export_progress.config(value=80)
                    self.export_status_label.config(text="Menyimpan file...")

                    # Add to history
                    self.add_to_history(
                        filename=filename,
                        format_type=self.format_mapping.get(self.format_var.get(), "PDF"),
                        estate=self.export_estate_var.get(),
                        status="Sukses"
                    )

                    # Complete
                    self.export_progress.config(value=100)
                    self.export_status_label.config(text="Laporan berhasil digenerate!")

                    # Show success message
                    messagebox.showinfo(
                        "Export Berhasil",
                        f"Laporan berhasil disimpan:\n{filepath}"
                    )

                    # Handle email sending if enabled
                    if self.send_email_var.get():
                        self.send_email_report(filepath)

                else:
                    raise Exception("Gagal generate laporan")

            else:
                # Fallback to simple file creation
                self.create_simple_report(filepath, export_config)

        except Exception as e:
            self.export_status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Export Error", f"Gagal generate laporan: {str(e)}")

            # Add to history with error status
            self.add_to_history(
                filename=filename if 'filename' in locals() else "Unknown",
                format_type=self.format_mapping.get(self.format_var.get(), "PDF"),
                estate=self.export_estate_var.get(),
                status="Error"
            )

        finally:
            self.generate_button.config(state=tk.NORMAL)

    def get_export_config(self) -> Dict[str, Any]:
        """Get export configuration"""
        return {
            'report_title': self.report_title_var.get(),
            'company_name': self.company_name_var.get(),
            'period': self.period_var.get(),
            'format_date': self.format_date_var.get(),
            'include_charts': self.include_charts_var.get(),
            'include_detailed_data': self.include_detailed_var.get(),
            'include_employee_analysis': self.include_employee_var.get(),
            'include_summary_only': self.include_summary_var.get(),
            'format_type': self.format_mapping.get(self.format_var.get(), "PDF"),
            'send_email': self.send_email_var.get(),
            'email_address': self.email_var.get() if self.send_email_var.get() else None,
            'compress': self.compress_var.get(),
            'export_individual': self.export_individual_var.get()
        }

    def create_simple_report(self, filepath: str, config: Dict[str, Any]):
        """Create a simple report (fallback method)"""
        # This would create a basic text/JSON report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {config['report_title']}\n\n")
            f.write(f"Company: {config['company_name']}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if self.analysis_results:
                f.write("## Analysis Results\n\n")
                f.write(json.dumps(self.analysis_results, indent=2, ensure_ascii=False, default=str))

    def preview_report(self):
        """Preview report before generating"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "Tidak ada data untuk dipreview")
            return

        # Create preview window
        preview_window = tk.Toplevel(self.parent)
        preview_window.title("Preview Laporan")
        preview_window.geometry("800x600")

        # Preview text
        preview_text = tk.Text(preview_window, wrap=tk.WORD, padx=10, pady=10)
        preview_text.pack(fill=tk.BOTH, expand=True)

        # Generate preview content
        config = self.get_export_config()
        preview_content = self.generate_preview_content(config)

        preview_text.insert(1.0, preview_content)
        preview_text.config(state=tk.DISABLED)

        # Close button
        close_button = ttk.Button(
            preview_window,
            text="Tutup",
            command=preview_window.destroy
        )
        close_button.pack(pady=10)

    def generate_preview_content(self, config: Dict[str, Any]) -> str:
        """Generate preview content"""
        content = f"PREVIEW LAPORAN\n"
        content += f"{'='*50}\n\n"
        content += f"Judul: {config['report_title']}\n"
        content += f"Perusahaan: {config['company_name']}\n"
        content += f"Format: {config['format_type']}\n"
        content += f"Estate: {self.export_estate_var.get()}\n"
        content += f"Periode: {config['period']}\n\n"

        content += f"Opsi Konten:\n"
        if config['include_charts']:
            content += f"- ✅ Sertakan Grafik\n"
        if config['include_employee_analysis']:
            content += f"- ✅ Analisis Performa Karyawan\n"
        if config['include_detailed_data']:
            content += f"- ✅ Data Detail Transaksi\n"
        if config['include_summary_only']:
            content += f"- ✅ Ringkasan Saja\n"

        content += f"\nInformasi Analysis:\n"
        if self.analysis_results:
            summary_stats = self.analysis_results.get('summary_statistics', {})
            content += f"- Total Transaksi: {summary_stats.get('total_transactions', 0):,}\n"
            content += f"- Tingkat Verifikasi: {summary_stats.get('verification_rate', 0):.1f}%\n"
            content += f"- Jumlah Perbedaan: {summary_stats.get('discrepancies', 0):,}\n"

        return content

    def save_template(self):
        """Save current export settings as template"""
        template_path = filedialog.asksaveasfilename(
            title="Simpan Template Export",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.export_path_var.get()
        )

        if template_path:
            try:
                template_data = self.get_export_config()
                template_data['export_path'] = self.export_path_var.get()
                template_data['filename_pattern'] = self.filename_pattern_var.get()
                template_data['selected_estate'] = self.export_estate_var.get()

                with open(template_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Sukses", "Template berhasil disimpan!")

            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan template: {str(e)}")

    def load_template(self):
        """Load export settings from template"""
        template_path = filedialog.askopenfilename(
            title="Load Template Export",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.export_path_var.get()
        )

        if template_path:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                # Apply template settings
                self.report_title_var.set(template_data.get('report_title', ''))
                self.company_name_var.set(template_data.get('company_name', ''))
                self.period_var.set(template_data.get('period', 'Otomatis'))
                self.format_date_var.set(template_data.get('format_date', True))
                self.export_path_var.set(template_data.get('export_path', ''))
                self.filename_pattern_var.set(template_data.get('filename_pattern', ''))
                self.export_estate_var.set(template_data.get('selected_estate', 'Semua'))

                self.include_charts_var.set(template_data.get('include_charts', True))
                self.include_detailed_var.set(template_data.get('include_detailed_data', False))
                self.include_employee_var.set(template_data.get('include_employee_analysis', True))
                self.include_summary_var.set(template_data.get('include_summary_only', False))

                # Find and set format
                format_type = template_data.get('format_type', 'PDF')
                for desc, fmt in self.format_mapping.items():
                    if fmt == format_type:
                        self.format_var.set(desc)
                        break

                messagebox.showinfo("Sukses", "Template berhasil dimuat!")

            except Exception as e:
                messagebox.showerror("Error", f"Gagal memuat template: {str(e)}")

    def send_email_report(self, filepath: str):
        """Send report via email (placeholder)"""
        email = self.email_var.get()
        # This would integrate with email functionality
        messagebox.showinfo(
            "Email",
            f"Fitur email akan mengirim laporan ke:\n{email}\n\n(File: {filepath})"
        )

    def add_to_history(self, filename: str, format_type: str, estate: str, status: str):
        """Add export record to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        export_id = len(self.export_history) + 1

        # Add to history list
        self.export_history.append({
            'id': export_id,
            'date': timestamp,
            'format': format_type,
            'estate': estate,
            'filename': filename,
            'status': status,
            'filepath': os.path.join(self.export_path_var.get(), filename)
        })

        # Add to treeview
        self.history_tree.insert('', 'end', text=str(export_id), values=(
            timestamp, format_type, estate, filename, status
        ))

        # Save history
        self.save_export_history()

    def load_export_history(self):
        """Load export history from file"""
        history_file = os.path.join(self.default_export_path, ".export_history.json")

        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.export_history = json.load(f)

                # Populate treeview
                for record in self.export_history:
                    self.history_tree.insert('', 'end', text=str(record['id']), values=(
                        record['date'], record['format'], record['estate'],
                        record['filename'], record['status']
                    ))

        except Exception as e:
            print(f"Error loading export history: {e}")

    def save_export_history(self):
        """Save export history to file"""
        history_file = os.path.join(self.default_export_path, ".export_history.json")

        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.export_history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving export history: {e}")

    def open_exported_file(self):
        """Open selected exported file"""
        selection = self.history_tree.selection()
        if not selection:
            return

        item = self.history_tree.item(selection[0])
        export_id = int(item['text'])

        # Find record in history
        record = next((r for r in self.export_history if r['id'] == export_id), None)
        if record and record.get('filepath'):
            try:
                os.startfile(record['filepath'])
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka file: {str(e)}")

    def open_export_folder(self):
        """Open export folder"""
        export_path = self.export_path_var.get()
        if os.path.exists(export_path):
            try:
                os.startfile(export_path)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka folder: {str(e)}")
        else:
            messagebox.showerror("Error", "Folder export tidak ditemukan")

    def clear_history(self):
        """Clear export history"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat export?"):
            # Clear treeview
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            # Clear history list
            self.export_history.clear()

            # Save empty history
            self.save_export_history()

            messagebox.showinfo("Sukses", "Riwayat export berhasil dihapus")

    def reset_widget(self):
        """Reset widget to initial state"""
        # Reset variables
        self.report_title_var.set(self.export_settings['report_title'])
        self.company_name_var.set(self.export_settings['company_name'])
        self.period_var.set("Otomatis")
        self.format_date_var.set(self.export_settings['format_date'])
        self.export_path_var.set(self.default_export_path)
        self.filename_pattern_var.set("FFB_Analysis_{estate}_{date}")
        self.export_estate_var.set("Semua")

        # Reset checkboxes
        self.include_charts_var.set(self.export_settings['include_charts'])
        self.include_detailed_var.set(self.export_settings['include_detailed_data'])
        self.include_employee_var.set(self.export_settings['include_employee_analysis'])
        self.include_summary_var.set(self.export_settings['include_summary_only'])

        # Reset other options
        self.send_email_var.set(False)
        self.compress_var.set(False)
        self.export_individual_var.set(False)

        # Reset progress
        self.export_progress.config(value=0)
        self.export_status_label.config(text="Siap untuk generate laporan")

        # Clear analysis results
        self.analysis_results = None
    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)
        elif hasattr(self, 'parent'):
            # For widgets that don't have main_container, just return
            pass

