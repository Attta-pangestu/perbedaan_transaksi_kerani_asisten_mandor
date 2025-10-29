#!/usr/bin/env python3
"""
Main GUI Application untuk Sistem Laporan FFB dengan Template Manager
Aplikasi desktop untuk generating laporan verifikasi transaksi FFB scanner
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import os
import sys
from datetime import datetime, date
import threading
import json
import logging
from typing import Dict, List, Any

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

# Import custom modules
from template_manager import TemplateManager
from report_generator import ReportGenerator
from ffb_analysis_engine import FFBAnalysisEngine

class FFBReportingSystemGUI:
    """Main GUI untuk sistem laporan FFB dengan template manager"""

    def __init__(self, root):
        self.root = root
        self.root.title("SISTEM LAPORAN VERIFIKASI FFB - Template Manager")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f0f0')

        # Resolve config file path - config.json is in the same directory as this script's parent
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(current_file)
        # config.json is in the same level as src, not parent of src
        config_dir = os.path.join(src_dir, "..")
        config_dir = os.path.abspath(config_dir)
        self.CONFIG_FILE = os.path.join(config_dir, "config.json")

        # Initialize components
        self.template_manager = TemplateManager()
        self.report_generator = ReportGenerator()
        self.analysis_engine = FFBAnalysisEngine()

        # Setup logging with absolute path
        logs_dir = os.path.join(config_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(logs_dir, 'app.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("FFBReportingSystemGUI initialized")

        # Load estates configuration
        self.estates = self.load_config()
        self.current_template = None

        # Setup UI
        self.setup_ui()
        self.load_templates()

    def load_config(self) -> Dict[str, str]:
        """Load konfigurasi estates dari file JSON"""
        default_estates = {
            "PGE 1A": r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB",
            "PGE 1B": r"C:\Users\nbgmf\Downloads\PTRJ_P1B\PTRJ_P1B.FDB",
            "PGE 2A": r"C:\Users\nbgmf\Downloads\IFESS_PGE_2A_19-06-2025",
            "PGE 2B": r"C:\Users\nbgmf\Downloads\IFESS_2B_19-06-2025\PTRJ_P2B.FDB",
            "IJL": r"C:\Users\nbgmf\Downloads\IFESS_IJL_19-06-2025\PTRJ_IJL_IMPIANJAYALESTARI.FDB",
            "DME": r"C:\Users\nbgmf\Downloads\IFESS_DME_19-06-2025\PTRJ_DME.FDB",
            "Are B2": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B2_19-06-2025\PTRJ_AB2.FDB",
            "Are B1": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B1_19-06-2025\PTRJ_AB1.FDB",
            "Are A": r"C:\Users\nbgmf\Downloads\IFESS_ARE_A_19-06-2025\PTRJ_ARA.FDB",
            "Are C": r"C:\Users\nbgmf\Downloads\IFESS_ARE_C_19-06-2025\PTRJ_ARC.FDB"
        }

        config_path = os.path.join(os.path.dirname(__file__), self.CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Error Konfigurasi", f"Gagal memuat {config_path}: {e}\nMenggunakan konfigurasi default.")
                return default_estates
        else:
            return default_estates

    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="SISTEM LAPORAN VERIFIKASI FFB - TEMPLATE MANAGER",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))

        # Create tabs
        self.create_report_tab()
        self.create_template_tab()
        self.create_config_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Siap untuk generate laporan")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def create_report_tab(self):
        """Create report generation tab"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="Generate Laporan")

        # Template selection
        template_frame = ttk.LabelFrame(report_frame, text="Pilih Template Laporan", padding="10")
        template_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(template_frame, text="Template:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, width=50, state='readonly')
        self.template_combo.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=(tk.W, tk.E))
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)

        template_frame.columnconfigure(1, weight=1)

        # Template info
        self.template_info = tk.Text(template_frame, height=4, width=60, wrap=tk.WORD)
        self.template_info.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Estate configuration
        estate_frame = ttk.LabelFrame(report_frame, text="Konfigurasi Database Estate", padding="10")
        estate_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Estate Treeview
        tree_frame = ttk.Frame(estate_frame)
        tree_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        columns = ('estate', 'path')
        self.estate_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=6)

        self.estate_tree.heading('estate', text='Estate')
        self.estate_tree.heading('path', text='Path Database')
        self.estate_tree.column('estate', width=150, anchor=tk.W)
        self.estate_tree.column('path', width=500, anchor=tk.W)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.estate_tree.yview)
        self.estate_tree.configure(yscrollcommand=scrollbar.set)

        self.estate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.populate_estate_tree()

        # Estate selection buttons
        btn_frame = ttk.Frame(estate_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Pilih Semua", command=self.select_all_estates).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hapus Pilihan", command=self.clear_estate_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ubah Path...", command=self.change_db_path).pack(side=tk.LEFT, padx=5)

        # Date range
        date_frame = ttk.LabelFrame(report_frame, text="Rentang Tanggal", padding="10")
        date_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(date_frame, text="Tanggal Mulai:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date = DateEntry(date_frame, width=20, background='darkblue', foreground='white')
        self.start_date.grid(row=0, column=1, padx=(10, 20), pady=5)

        ttk.Label(date_frame, text="Tanggal Akhir:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.end_date = DateEntry(date_frame, width=20, background='darkblue', foreground='white')
        self.end_date.grid(row=0, column=3, padx=(10, 0), pady=5)

        # Set default dates
        self.start_date.set_date(date(2025, 5, 1))
        self.end_date.set_date(date(2025, 5, 31))

        # Template parameters (dynamic)
        self.params_frame = ttk.LabelFrame(report_frame, text="Parameter Template", padding="10")
        self.params_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Progress
        progress_frame = ttk.LabelFrame(report_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        self.progress_var = tk.StringVar(value="Siap untuk generate laporan")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # Log
        log_frame = ttk.LabelFrame(report_frame, text="Log Proses", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))

        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.log_text = tk.Text(text_frame, height=10, width=80)
        log_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(report_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Generate Laporan", command=self.start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Buka Folder Output", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)

    def create_template_tab(self):
        """Create template management tab"""
        template_frame = ttk.Frame(self.notebook)
        self.notebook.add(template_frame, text="Template Manager")

        # Template list
        list_frame = ttk.LabelFrame(template_frame, text="Daftar Template", padding="10")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10), pady=10)

        columns = ('id', 'name', 'category', 'version')
        self.template_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        self.template_tree.heading('id', text='Template ID')
        self.template_tree.heading('name', text='Nama Template')
        self.template_tree.heading('category', text='Kategori')
        self.template_tree.heading('version', text='Versi')

        self.template_tree.column('id', width=150)
        self.template_tree.column('name', width=250)
        self.template_tree.column('category', width=150)
        self.template_tree.column('version', width=100)

        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.template_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Template details
        details_frame = ttk.LabelFrame(template_frame, text="Detail Template", padding="10")
        details_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        self.template_details = tk.Text(details_frame, height=20, width=50, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.template_details.yview)
        self.template_details.configure(yscrollcommand=details_scrollbar.set)

        self.template_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Template actions
        actions_frame = ttk.Frame(template_frame)
        actions_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(actions_frame, text="Refresh Templates", command=self.refresh_templates).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="View Selected", command=self.view_template_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Create New", command=self.create_new_template).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        template_frame.columnconfigure(0, weight=1)
        template_frame.columnconfigure(1, weight=1)
        template_frame.rowconfigure(0, weight=1)

    def create_config_tab(self):
        """Create configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Konfigurasi")

        # Database configuration
        db_frame = ttk.LabelFrame(config_frame, text="Konfigurasi Database", padding="10")
        db_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(db_frame, text="File konfigurasi: config.json").pack(anchor=tk.W)
        ttk.Label(db_frame, text="Lokasi: ../../config.json").pack(anchor=tk.W)

        ttk.Button(db_frame, text="Edit Konfigurasi Manual", command=self.edit_config).pack(pady=10)

        # System info
        info_frame = ttk.LabelFrame(config_frame, text="Informasi Sistem", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        info_text = f"""
        Sistem Laporan FFB - Template Manager

        Versi: 1.0.0
        Template Directory: templates/
        Output Directory: reports/
        Log Directory: logs/

        Komponen:
        - Template Manager: Mengelola template laporan
        - Report Generator: Generate laporan PDF/Excel
        - Analysis Engine: Logic analisis transaksi
        - GUI Interface: Interface pengguna desktop
        """

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

    def load_templates(self):
        """Load templates ke combo box dan tree"""
        templates = self.template_manager.get_all_templates()

        # Update combo box
        choices = self.template_manager.get_template_choices()
        self.template_combo['values'] = [choice[1] for choice in choices]

        # Update tree
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)

        for template in templates:
            self.template_tree.insert('', tk.END, values=(
                template['template_id'],
                template['name'],
                template['category'],
                template['version']
            ))

    def on_template_selected(self, event):
        """Handle template selection"""
        selected_text = self.template_var.get()

        # Find template by display text
        choices = self.template_manager.get_template_choices()
        template_id = None
        for tid, display_text in choices:
            if display_text == selected_text:
                template_id = tid
                break

        if template_id:
            self.current_template = self.template_manager.get_template(template_id)
            self.display_template_info()
            self.create_parameter_controls()

    def display_template_info(self):
        """Display informasi template yang dipilih"""
        if not self.current_template:
            return

        info_text = f"""
Nama: {self.current_template.get('name', 'Unknown')}
Deskripsi: {self.current_template.get('description', 'No description')}
Kategori: {self.current_template.get('category', 'Unknown')}
Versi: {self.current_template.get('version', 'Unknown')}
Dibuat: {self.current_template.get('created_date', 'Unknown')}
        """

        self.template_info.delete(1.0, tk.END)
        self.template_info.insert(1.0, info_text.strip())

    def create_parameter_controls(self):
        """Create dynamic parameter controls based on template"""
        # Clear existing controls
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        if not self.current_template:
            return

        parameters = self.current_template.get('parameters', [])
        self.param_vars = {}

        row = 0
        for param in parameters:
            param_name = param['name']
            param_type = param['type']
            display_name = param['display_name']

            ttk.Label(self.params_frame, text=f"{display_name}:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))

            if param_type == 'BOOLEAN':
                var = tk.BooleanVar(value=param.get('default_value', False))
                widget = ttk.Checkbutton(self.params_frame, variable=var)
            elif param_type == 'MULTI_SELECT':
                var = tk.StringVar()
                frame = ttk.Frame(self.params_frame)
                widget = frame

                options = param.get('options', [])
                for i, option in enumerate(options):
                    cb = ttk.Checkbutton(
                        frame,
                        text=option['label'],
                        value=option['value'],
                        command=lambda val=option['value'], v=var: self.update_multi_select(v, val)
                    )
                    cb.grid(row=i//3, column=i%3, sticky=tk.W, padx=5, pady=2)
            else:
                var = tk.StringVar(value=param.get('default_value', ''))
                widget = ttk.Entry(self.params_frame, textvariable=var, width=30)

            widget.grid(row=row, column=1, sticky=tk.W, pady=5)
            self.param_vars[param_name] = var
            row += 1

    def update_multi_select(self, var, value):
        """Update multi-select parameter value"""
        current = var.get().split(',') if var.get() else []
        if value in current:
            current.remove(value)
        else:
            current.append(value)
        var.set(','.join(current))

    def populate_estate_tree(self):
        """Populate estate tree dengan data konfigurasi"""
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)

        for estate_name, db_path in self.estates.items():
            self.estate_tree.insert('', tk.END, values=(estate_name, db_path))

    def select_all_estates(self):
        for item in self.estate_tree.get_children():
            self.estate_tree.selection_add(item)

    def clear_estate_selection(self):
        self.estate_tree.selection_remove(self.estate_tree.selection())

    def change_db_path(self):
        selected_item = self.estate_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Silakan pilih satu estate untuk diubah path-nya.")
            return

        new_path = filedialog.askopenfilename(
            title="Pilih File Database (.FDB)",
            filetypes=[("Firebird Database", "*.fdb")]
        )

        if new_path:
            self.estate_tree.item(selected_item, values=(self.estate_tree.item(selected_item, 'values')[0], new_path))
            self.log_message(f"Path untuk {self.estate_tree.item(selected_item, 'values')[0]} diubah.")

    def start_analysis(self):
        """Start analysis and report generation"""
        if not self.current_template:
            messagebox.showerror("Error", "Silakan pilih template laporan terlebih dahulu.")
            return

        selected_indices = self.estate_tree.selection()
        if not selected_indices:
            messagebox.showerror("Error", "Silakan pilih minimal satu estate")
            return

        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()

        if start_date > end_date:
            messagebox.showerror("Error Tanggal", "Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
            return

        # Start analysis in thread
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()

    def run_analysis(self):
        """Run analysis and generate report"""
        try:
            selected_items = self.estate_tree.selection()
            selected_estates = []
            for item_id in selected_items:
                values = self.estate_tree.item(item_id, 'values')
                estate_name = values[0]
                db_path = values[1]
                selected_estates.append((estate_name, db_path))

            if not selected_estates:
                messagebox.showerror("Error", "Silakan pilih minimal satu estate dari daftar.")
                return

            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()

            # Get parameter values
            parameters = {
                'START_DATE': start_date,
                'END_DATE': end_date,
                'ESTATES': [estate[0] for estate in selected_estates]
            }

            # Add template parameters
            if hasattr(self, 'param_vars'):
                for param_name, var in self.param_vars.items():
                    if hasattr(var, 'get'):
                        parameters[param_name] = var.get()

            self.log_message("=== GENERATING REPORT ===")
            self.log_message(f"Template: {self.current_template['name']}")
            self.log_message(f"Periode: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")
            self.log_message(f"Jumlah Estate: {len(selected_estates)}")

            self.progress_bar['maximum'] = len(selected_estates)
            all_results = []

            for i, (estate_name, db_path) in enumerate(selected_estates):
                self.progress_var.set(f"Menganalisis {estate_name}")
                self.progress_bar['value'] = i
                self.root.update_idletasks()

                try:
                    use_status_704_filter = parameters.get('USE_STATUS_704_FILTER', False)
                    estate_results = self.analysis_engine.analyze_estate(
                        estate_name, db_path, start_date, end_date, use_status_704_filter
                    )
                    if estate_results:
                        all_results.extend(estate_results)
                        self.log_message(f"{estate_name}: {len(estate_results)} divisi")
                    else:
                        self.log_message(f"{estate_name}: Tidak ada data")
                except Exception as e:
                    self.log_message(f"{estate_name}: {str(e)}")

            if all_results:
                self.log_message("Generating PDF report...")
                pdf_path = self.report_generator.generate_pdf_report(
                    self.current_template, all_results, parameters
                )
                self.log_message(f"Laporan PDF: {pdf_path}")
                messagebox.showinfo("Sukses", f"Laporan berhasil digenerate!\n\nFile: {pdf_path}")
            else:
                self.log_message("Tidak ada data untuk di-generate")
                messagebox.showwarning("Warning", "Tidak ada data yang dapat diproses untuk laporan.")

            self.progress_var.set("Analisis selesai")

        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Terjadi error saat generate laporan:\n\n{str(e)}")

    def log_message(self, message):
        """Log message ke log widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def open_output_folder(self):
        output_dir = self.report_generator.output_dir
        if os.path.exists(output_dir):
            os.startfile(output_dir)

    def refresh_templates(self):
        """Refresh template list"""
        self.template_manager._load_templates()
        self.load_templates()
        self.log_message("Template list refreshed")

    def view_template_details(self):
        """View selected template details"""
        selected_item = self.template_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Silakan pilih template dari daftar.")
            return

        values = self.template_tree.item(selected_item, 'values')
        template_id = values[0]

        template = self.template_manager.get_template(template_id)
        if template:
            details = json.dumps(template, indent=2, ensure_ascii=False)
            self.template_details.delete(1.0, tk.END)
            self.template_details.insert(1.0, details)

    def create_new_template(self):
        """Create new template (placeholder)"""
        messagebox.showinfo("Info", "Template editor akan segera tersedia")

    def edit_config(self):
        """Edit configuration file"""
        config_path = os.path.join(os.path.dirname(__file__), self.CONFIG_FILE)
        if os.path.exists(config_path):
            os.startfile(config_path)
        else:
            messagebox.showinfo("Info", f"File konfigurasi tidak ditemukan: {config_path}")


def main():
    """Main function"""
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)

    root = tk.Tk()
    app = FFBReportingSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()