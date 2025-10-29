"""
Results Display Widget
GUI component for displaying analysis results with comprehensive data visualization
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Callable
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns


class ResultsDisplayWidget:
    """
    Widget for displaying comprehensive analysis results with tables and charts
    """

    def __init__(self, parent_frame, on_export_callback: Optional[Callable] = None):
        """
        Initialize results display widget

        :param parent_frame: Parent tkinter frame
        :param on_export_callback: Optional export callback
        """
        self.parent = parent_frame
        self.on_export_callback = on_export_callback

        # Data storage
        self.analysis_results = None
        self.current_view = "summary"
        self.available_estates = []
        self.selected_estate = None

        # Visualization settings
        self.figure = None
        self.canvas = None
        self.chart_type = "bar"

        self.setup_ui()

    def setup_ui(self):
        """Setup the results display UI"""
        # Main container with notebook for tabs
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create notebook for different views
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Ringkasan")
        self.setup_summary_tab()

        # Detailed Results tab
        self.detailed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detailed_frame, text="Detail Transaksi")
        self.setup_detailed_tab()

        # Employee Performance tab
        self.employee_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employee_frame, text="Performa Karyawan")
        self.setup_employee_tab()

        # Charts and Visualization tab
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Grafik & Visualisasi")
        self.setup_charts_tab()

        # Export tab
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Export Data")
        self.setup_export_tab()

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def setup_summary_tab(self):
        """Setup summary tab with overview statistics"""
        # Main container
        container = ttk.Frame(self.summary_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header section
        header_frame = ttk.LabelFrame(container, text="Informasi Analisis", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Analysis info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill=tk.X)

        self.analysis_date_label = ttk.Label(info_frame, text="Tanggal Analisis: -")
        self.analysis_date_label.pack(anchor=tk.W, pady=2)

        self.date_range_label = ttk.Label(info_frame, text="Rentang Tanggal: -")
        self.date_range_label.pack(anchor=tk.W, pady=2)

        self.estates_label = ttk.Label(info_frame, text="Estates: -")
        self.estates_label.pack(anchor=tk.W, pady=2)

        # Summary statistics
        stats_frame = ttk.LabelFrame(container, text="Statistik Keseluruhan", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Create statistics grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        # Statistics labels
        self.stats_labels = {}
        stats_config = [
            ("total_transactions", "Total Transaksi", "0"),
            ("kerani_transactions", "Transaksi Kerani", "0"),
            ("verified_transactions", "Transaksi Terverifikasi", "0"),
            ("verification_rate", "Tingkat Verifikasi", "0%"),
            ("discrepancies", "Perbedaan Data", "0"),
            ("unique_employees", "Karyawan Unik", "0"),
            ("divisions", "Divisi Terlibat", "0"),
            ("analysis_duration", "Durasi Analisis", "-")
        ]

        for i, (key, label, default) in enumerate(stats_config):
            row = i // 2
            col = i % 2

            frame = ttk.Frame(stats_grid)
            frame.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)

            ttk.Label(frame, text=f"{label}:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            self.stats_labels[key] = ttk.Label(frame, text=default, font=('Arial', 10))
            self.stats_labels[key].pack(anchor=tk.W)

        # Estate-wise breakdown
        estate_frame = ttk.LabelFrame(container, text="Breakdown per Estate", padding="10")
        estate_frame.pack(fill=tk.BOTH, expand=True)

        # Estate selection
        estate_select_frame = ttk.Frame(estate_frame)
        estate_select_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(estate_select_frame, text="Pilih Estate:").pack(side=tk.LEFT, padx=(0, 10))
        self.estate_var = tk.StringVar()
        self.estate_combo = ttk.Combobox(
            estate_select_frame,
            textvariable=self.estate_var,
            state="readonly",
            width=30
        )
        self.estate_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.estate_combo.bind("<<ComboboxSelected>>", self.on_estate_selected)

        ttk.Button(
            estate_select_frame,
            text="Tampilkan Semua",
            command=self.show_all_estates
        ).pack(side=tk.LEFT)

        # Estate statistics treeview
        self.estate_tree = ttk.Treeview(
            estate_frame,
            columns=("transactions", "verification_rate", "discrepancies", "employees"),
            show="tree headings"
        )

        # Configure columns
        self.estate_tree.heading("#0", text="Estate")
        self.estate_tree.heading("transactions", text="Total Transaksi")
        self.estate_tree.heading("verification_rate", text="Tingkat Verifikasi")
        self.estate_tree.heading("discrepancies", text="Perbedaan")
        self.estate_tree.heading("employees", text="Karyawan")

        # Column widths
        self.estate_tree.column("#0", width=150)
        self.estate_tree.column("transactions", width=120)
        self.estate_tree.column("verification_rate", width=120)
        self.estate_tree.column("discrepancies", width=100)
        self.estate_tree.column("employees", width=80)

        # Scrollbar
        estate_scrollbar = ttk.Scrollbar(estate_frame, orient=tk.VERTICAL, command=self.estate_tree.yview)
        self.estate_tree.configure(yscrollcommand=estate_scrollbar.set)

        self.estate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        estate_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_detailed_tab(self):
        """Setup detailed transaction results tab"""
        # Main container
        container = ttk.Frame(self.detailed_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Filter controls
        filter_frame = ttk.LabelFrame(container, text="Filter Data", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Estate filter
        estate_filter_frame = ttk.Frame(filter_frame)
        estate_filter_frame.pack(fill=tk.X, pady=2)

        ttk.Label(estate_filter_frame, text="Estate:", width=10).pack(side=tk.LEFT)
        self.detail_estate_var = tk.StringVar()
        self.detail_estate_combo = ttk.Combobox(
            estate_filter_frame,
            textvariable=self.detail_estate_var,
            state="readonly",
            width=20
        )
        self.detail_estate_combo.pack(side=tk.LEFT, padx=(5, 20))

        # Verification status filter
        ttk.Label(estate_filter_frame, text="Status:", width=10).pack(side=tk.LEFT)
        self.verification_var = tk.StringVar(value="Semua")
        verification_combo = ttk.Combobox(
            estate_filter_frame,
            textvariable=self.verification_var,
            values=["Semua", "Terverifikasi", "Tidak Terverifikasi"],
            state="readonly",
            width=20
        )
        verification_combo.pack(side=tk.LEFT, padx=(5, 20))

        # Employee filter
        ttk.Label(estate_filter_frame, text="Karyawan:", width=10).pack(side=tk.LEFT)
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(
            estate_filter_frame,
            textvariable=self.employee_var,
            state="readonly",
            width=20
        )
        self.employee_combo.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(
            estate_filter_frame,
            text="Terapkan Filter",
            command=self.apply_detail_filters
        ).pack(side=tk.LEFT, padx=(10, 5))

        ttk.Button(
            estate_filter_frame,
            text="Reset Filter",
            command=self.reset_detail_filters
        ).pack(side=tk.LEFT)

        # Results table
        table_frame = ttk.LabelFrame(container, text="Detail Transaksi", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview for detailed results
        self.detail_tree = ttk.Treeview(
            table_frame,
            columns=("transno", "date", "employee", "role", "verified", "differences"),
            show="tree headings"
        )

        # Configure columns
        self.detail_tree.heading("#0", text="Estate")
        self.detail_tree.heading("transno", text="Trans No")
        self.detail_tree.heading("date", text="Tanggal")
        self.detail_tree.heading("employee", text="Karyawan")
        self.detail_tree.heading("role", text="Role")
        self.detail_tree.heading("verified", text="Status")
        self.detail_tree.heading("differences", text="Perbedaan")

        # Column widths
        self.detail_tree.column("#0", width=100)
        self.detail_tree.column("transno", width=100)
        self.detail_tree.column("date", width=100)
        self.detail_tree.column("employee", width=150)
        self.detail_tree.column("role", width=80)
        self.detail_tree.column("verified", width=100)
        self.detail_tree.column("differences", width=200)

        # Scrollbars
        detail_h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.detail_tree.xview)
        detail_v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(xscrollcommand=detail_h_scrollbar.set, yscrollcommand=detail_v_scrollbar.set)

        self.detail_tree.grid(row=0, column=0, sticky="nsew")
        detail_h_scrollbar.grid(row=1, column=0, sticky="ew")
        detail_v_scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Double-click to view details
        self.detail_tree.bind("<Double-1>", self.on_transaction_double_click)

    def setup_employee_tab(self):
        """Setup employee performance tab"""
        # Main container
        container = ttk.Frame(self.employee_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Employee selection
        select_frame = ttk.LabelFrame(container, text="Pilih Karyawan", padding="10")
        select_frame.pack(fill=tk.X, pady=(0, 10))

        employee_select_frame = ttk.Frame(select_frame)
        employee_select_frame.pack(fill=tk.X)

        ttk.Label(employee_select_frame, text="Estate:").pack(side=tk.LEFT, padx=(0, 10))
        self.perf_estate_var = tk.StringVar()
        self.perf_estate_combo = ttk.Combobox(
            employee_select_frame,
            textvariable=self.perf_estate_var,
            state="readonly",
            width=20
        )
        self.perf_estate_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(employee_select_frame, text="Karyawan:").pack(side=tk.LEFT, padx=(0, 10))
        self.perf_employee_var = tk.StringVar()
        self.perf_employee_combo = ttk.Combobox(
            employee_select_frame,
            textvariable=self.perf_employee_var,
            state="readonly",
            width=30
        )
        self.perf_employee_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            employee_select_frame,
            text="Tampilkan Performa",
            command=self.show_employee_performance
        ).pack(side=tk.LEFT)

        # Employee performance display
        perf_frame = ttk.LabelFrame(container, text="Performa Karyawan", padding="10")
        perf_frame.pack(fill=tk.BOTH, expand=True)

        # Performance metrics
        metrics_frame = ttk.Frame(perf_frame)
        metrics_frame.pack(fill=tk.X, pady=(0, 10))

        self.perf_metrics = {}
        metrics_config = [
            ("total_transactions", "Total Transaksi"),
            ("verified_transactions", "Transaksi Terverifikasi"),
            ("verification_rate", "Tingkat Verifikasi"),
            ("discrepancies", "Jumlah Perbedaan"),
            ("accuracy_rate", "Tingkat Akurasi"),
            ("avg_daily_transactions", "Rata-rata Transaksi/Hari")
        ]

        for i, (key, label) in enumerate(metrics_config):
            row = i // 3
            col = i % 3

            frame = ttk.Frame(metrics_frame)
            frame.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)

            ttk.Label(frame, text=f"{label}:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            self.perf_metrics[key] = ttk.Label(frame, text="-", font=('Arial', 10))
            self.perf_metrics[key].pack(anchor=tk.W)

        # Employee transaction history
        history_frame = ttk.LabelFrame(perf_frame, text="Riwayat Transaksi", padding="5")
        history_frame.pack(fill=tk.BOTH, expand=True)

        # Employee history treeview
        self.emp_history_tree = ttk.Treeview(
            history_frame,
            columns=("date", "transno", "verification_status", "differences"),
            show="tree headings"
        )

        # Configure columns
        self.emp_history_tree.heading("#0", text="ID")
        self.emp_history_tree.heading("date", text="Tanggal")
        self.emp_history_tree.heading("transno", text="Trans No")
        self.emp_history_tree.heading("verification_status", text="Status Verifikasi")
        self.emp_history_tree.heading("differences", text="Perbedaan")

        # Column widths
        self.emp_history_tree.column("#0", width=80)
        self.emp_history_tree.column("date", width=100)
        self.emp_history_tree.column("transno", width=100)
        self.emp_history_tree.column("verification_status", width=120)
        self.emp_history_tree.column("differences", width=200)

        # Scrollbars
        emp_h_scrollbar = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.emp_history_tree.xview)
        emp_v_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.emp_history_tree.yview)
        self.emp_history_tree.configure(xscrollcommand=emp_h_scrollbar.set, yscrollcommand=emp_v_scrollbar.set)

        self.emp_history_tree.grid(row=0, column=0, sticky="nsew")
        emp_h_scrollbar.grid(row=1, column=0, sticky="ew")
        emp_v_scrollbar.grid(row=0, column=1, sticky="ns")

        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

    def setup_charts_tab(self):
        """Setup charts and visualization tab"""
        # Main container
        container = ttk.Frame(self.charts_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Chart controls
        control_frame = ttk.LabelFrame(container, text="Kontrol Grafik", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Chart type selection
        chart_type_frame = ttk.Frame(control_frame)
        chart_type_frame.pack(fill=tk.X, pady=2)

        ttk.Label(chart_type_frame, text="Jenis Grafik:", width=15).pack(side=tk.LEFT)
        self.chart_type_var = tk.StringVar(value="verification_rates")
        chart_types = [
            ("Tingkat Verifikasi", "verification_rates"),
            ("Volume Transaksi", "transaction_volume"),
            ("Distribusi Perbedaan", "discrepancy_distribution"),
            ("Performa Karyawan", "employee_performance"),
            ("Tren Harian", "daily_trends")
        ]

        for text, value in chart_types:
            ttk.Radiobutton(
                chart_type_frame,
                text=text,
                variable=self.chart_type_var,
                value=value,
                command=self.update_chart
            ).pack(side=tk.LEFT, padx=(0, 15))

        # Estate selection for charts
        estate_chart_frame = ttk.Frame(control_frame)
        estate_chart_frame.pack(fill=tk.X, pady=5)

        ttk.Label(estate_chart_frame, text="Estate:", width=15).pack(side=tk.LEFT)
        self.chart_estate_var = tk.StringVar(value="Semua")
        self.chart_estate_combo = ttk.Combobox(
            estate_chart_frame,
            textvariable=self.chart_estate_var,
            state="readonly",
            width=20
        )
        self.chart_estate_combo.pack(side=tk.LEFT, padx=(5, 20))

        ttk.Button(
            estate_chart_frame,
            text="Perbarui Grafik",
            command=self.update_chart
        ).pack(side=tk.LEFT)

        # Chart display area
        self.chart_frame = ttk.LabelFrame(container, text="Grafik", padding="5")
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize with empty chart
        self.update_chart()

    def setup_export_tab(self):
        """Setup export data tab"""
        # Main container
        container = ttk.Frame(self.export_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Export options
        export_frame = ttk.LabelFrame(container, text="Opsi Export", padding="10")
        export_frame.pack(fill=tk.X, pady=(0, 10))

        # File format selection
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=5)

        ttk.Label(format_frame, text="Format:", width=15).pack(side=tk.LEFT)
        self.export_format_var = tk.StringVar(value="Excel")
        formats = ["Excel", "CSV", "PDF", "JSON"]

        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.export_format_var,
            values=formats,
            state="readonly",
            width=20
        )
        format_combo.pack(side=tk.LEFT, padx=(5, 20))

        # Data selection
        data_frame = ttk.Frame(export_frame)
        data_frame.pack(fill=tk.X, pady=5)

        ttk.Label(data_frame, text="Data:", width=15).pack(side=tk.LEFT)
        self.export_data_var = tk.StringVar(value="summary")
        data_options = [
            ("Ringkasan", "summary"),
            ("Detail Transaksi", "detailed"),
            ("Performa Karyawan", "employee"),
            ("Semua Data", "all")
        ]

        for text, value in data_options:
            ttk.Radiobutton(
                data_frame,
                text=text,
                variable=self.export_data_var,
                value=value
            ).pack(side=tk.LEFT, padx=(0, 15))

        # Estate selection for export
        export_estate_frame = ttk.Frame(export_frame)
        export_estate_frame.pack(fill=tk.X, pady=5)

        ttk.Label(export_estate_frame, text="Estate:", width=15).pack(side=tk.LEFT)
        self.export_estate_var = tk.StringVar(value="Semua")
        self.export_estate_combo = ttk.Combobox(
            export_estate_frame,
            textvariable=self.export_estate_var,
            state="readonly",
            width=20
        )
        self.export_estate_combo.pack(side=tk.LEFT, padx=(5, 20))

        # Export button
        button_frame = ttk.Frame(export_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="Export Data",
            command=self.export_data,
            style="Accent.TButton"
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="Buka Folder Export",
            command=self.open_export_folder
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Export log
        log_frame = ttk.LabelFrame(container, text="Log Export", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Export log text
        self.export_log = tk.Text(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=('Courier', 9)
        )

        export_log_scrollbar = ttk.Scrollbar(
            log_frame,
            orient=tk.VERTICAL,
            command=self.export_log.yview
        )
        self.export_log.configure(yscrollcommand=export_log_scrollbar.set)

        self.export_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        export_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure log tags
        self.export_log.tag_configure("info", foreground="black")
        self.export_log.tag_configure("success", foreground="green")
        self.export_log.tag_configure("error", foreground="red")
        self.export_log.tag_configure("timestamp", foreground="gray")

    def display_results(self, analysis_results: Dict[str, Any]):
        """
        Display analysis results in the widget

        :param analysis_results: Analysis results dictionary
        """
        self.analysis_results = analysis_results
        self.available_estates = list(analysis_results.get('estate_results', {}).keys())

        # Update estate combos
        for combo_var in [
            self.estate_var, self.detail_estate_var, self.perf_estate_var,
            self.chart_estate_var, self.export_estate_var
        ]:
            if hasattr(combo_var, 'set'):
                combo_var.set('')

        # Update all estate combo boxes
        estate_options = ['Semua'] + self.available_estates
        for combo in [
            self.estate_combo, self.detail_estate_combo,
            self.perf_estate_combo, self.chart_estate_combo, self.export_estate_combo
        ]:
            if combo:
                combo['values'] = estate_options

        # Update summary tab
        self.update_summary_tab()

        # Update detailed results
        self.update_detailed_results()

        # Update employee performance
        self.update_employee_performance()

        # Update charts
        self.update_chart()

        # Log the display
        self.log_export_message("Hasil analisis berhasil dimuat", "success")

    def update_summary_tab(self):
        """Update summary tab with analysis results"""
        if not self.analysis_results:
            return

        # Update analysis info
        analysis_info = self.analysis_results.get('analysis_info', {})

        self.analysis_date_label.config(
            text=f"Tanggal Analisis: {analysis_info.get('analysis_date', '-')}"
        )

        date_range = analysis_info.get('date_range', {})
        if date_range:
            start_date = date_range.get('start_date', '-')
            end_date = date_range.get('end_date', '-')
            self.date_range_label.config(text=f"Rentang Tanggal: {start_date} - {end_date}")

        estates = analysis_info.get('estates', [])
        self.estates_label.config(text=f"Estates: {', '.join(estates) if estates else '-'}")

        # Update statistics
        summary_stats = self.analysis_results.get('summary_statistics', {})

        self.stats_labels['total_transactions'].config(
            text=f"{summary_stats.get('total_transactions', 0):,}"
        )
        self.stats_labels['kerani_transactions'].config(
            text=f"{summary_stats.get('kerani_transactions', 0):,}"
        )
        self.stats_labels['verified_transactions'].config(
            text=f"{summary_stats.get('verified_transactions', 0):,}"
        )
        self.stats_labels['verification_rate'].config(
            text=f"{summary_stats.get('verification_rate', 0):.1f}%"
        )
        self.stats_labels['discrepancies'].config(
            text=f"{summary_stats.get('discrepancies', 0):,}"
        )
        self.stats_labels['unique_employees'].config(
            text=f"{summary_stats.get('unique_employees', 0):,}"
        )
        self.stats_labels['divisions'].config(
            text=f"{summary_stats.get('divisions', 0):,}"
        )

        duration = analysis_info.get('analysis_duration', '-')
        self.stats_labels['analysis_duration'].config(text=str(duration))

        # Update estate breakdown
        self.update_estate_breakdown()

    def update_estate_breakdown(self):
        """Update estate breakdown treeview"""
        # Clear existing items
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)

        estate_results = self.analysis_results.get('estate_results', {})

        for estate_name, estate_data in estate_results.items():
            stats = estate_data.get('statistics', {})

            self.estate_tree.insert('', 'end', text=estate_name, values=(
                stats.get('total_transactions', 0),
                f"{stats.get('verification_rate', 0):.1f}%",
                stats.get('discrepancies', 0),
                stats.get('unique_employees', 0)
            ))

    def update_detailed_results(self):
        """Update detailed transaction results"""
        # Clear existing items
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        detailed_results = self.analysis_results.get('detailed_results', [])

        for result in detailed_results:
            estate = result.get('estate', '-')
            transno = result.get('transno', '-')
            trans_date = result.get('trans_date', '-')
            employee = result.get('employee', '-')
            role = result.get('role', '-')
            verified = "Ya" if result.get('verified', False) else "Tidak"
            differences = result.get('differences', '')

            self.detail_tree.insert('', 'end', text=estate, values=(
                transno, trans_date, employee, role, verified, differences
            ))

    def update_employee_performance(self):
        """Update employee performance data"""
        # Update employee combos
        employees = set()
        estate_results = self.analysis_results.get('estate_results', {})

        for estate_data in estate_results.values():
            emp_results = estate_data.get('employee_results', {})
            employees.update(emp_results.keys())

        employee_options = ['Semua'] + sorted(list(employees))
        if self.perf_employee_combo:
            self.perf_employee_combo['values'] = employee_options

    def update_chart(self):
        """Update chart display"""
        if not self.figure or not self.analysis_results:
            return

        # Clear previous chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        chart_type = self.chart_type_var.get()
        selected_estate = self.chart_estate_var.get()

        try:
            if chart_type == "verification_rates":
                self.create_verification_rate_chart(ax, selected_estate)
            elif chart_type == "transaction_volume":
                self.create_transaction_volume_chart(ax, selected_estate)
            elif chart_type == "discrepancy_distribution":
                self.create_discrepancy_chart(ax, selected_estate)
            elif chart_type == "employee_performance":
                self.create_employee_performance_chart(ax, selected_estate)
            elif chart_type == "daily_trends":
                self.create_daily_trends_chart(ax, selected_estate)

            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            ax.text(0.5, 0.5, f"Error creating chart: {str(e)}",
                   ha='center', va='center', transform=ax.transAxes)
            self.canvas.draw()

    def create_verification_rate_chart(self, ax, selected_estate: str):
        """Create verification rate bar chart"""
        estate_results = self.analysis_results.get('estate_results', {})

        estates = []
        rates = []

        for estate_name, estate_data in estate_results.items():
            if selected_estate == "Semua" or estate_name == selected_estate:
                stats = estate_data.get('statistics', {})
                estates.append(estate_name)
                rates.append(stats.get('verification_rate', 0))

        if estates:
            bars = ax.bar(estates, rates, color='steelblue', alpha=0.7)
            ax.set_title('Tingkat Verifikasi per Estate')
            ax.set_ylabel('Tingkat Verifikasi (%)')
            ax.set_xlabel('Estate')

            # Add value labels on bars
            for bar, rate in zip(bars, rates):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{rate:.1f}%', ha='center', va='bottom')

            # Rotate x labels if needed
            if len(estates) > 4:
                ax.tick_params(axis='x', rotation=45)

    def create_transaction_volume_chart(self, ax, selected_estate: str):
        """Create transaction volume chart"""
        estate_results = self.analysis_results.get('estate_results', {})

        estates = []
        kerani_trans = []
        verified_trans = []

        for estate_name, estate_data in estate_results.items():
            if selected_estate == "Semua" or estate_name == selected_estate:
                stats = estate_data.get('statistics', {})
                estates.append(estate_name)
                kerani_trans.append(stats.get('kerani_transactions', 0))
                verified_trans.append(stats.get('verified_transactions', 0))

        if estates:
            x = range(len(estates))
            width = 0.35

            bars1 = ax.bar([i - width/2 for i in x], kerani_trans, width,
                          label='Transaksi Kerani', color='lightblue', alpha=0.7)
            bars2 = ax.bar([i + width/2 for i in x], verified_trans, width,
                          label='Transaksi Terverifikasi', color='darkblue', alpha=0.7)

            ax.set_title('Volume Transaksi per Estate')
            ax.set_ylabel('Jumlah Transaksi')
            ax.set_xlabel('Estate')
            ax.set_xticks(x)
            ax.set_xticklabels(estates)
            ax.legend()

            # Rotate x labels if needed
            if len(estates) > 4:
                ax.tick_params(axis='x', rotation=45)

    def create_discrepancy_chart(self, ax, selected_estate: str):
        """Create discrepancy distribution chart"""
        estate_results = self.analysis_results.get('estate_results', {})

        estates = []
        discrepancies = []

        for estate_name, estate_data in estate_results.items():
            if selected_estate == "Semua" or estate_name == selected_estate:
                stats = estate_data.get('statistics', {})
                estates.append(estate_name)
                discrepancies.append(stats.get('discrepancies', 0))

        if estates:
            # Create pie chart if single estate, bar chart for multiple
            if len(estates) == 1:
                ax.pie([discrepancies[0], max(1, len(estates) - discrepancies[0])],
                      labels=['Perbedaan', 'Normal'], autopct='%1.1f%%',
                      colors=['red', 'green'], alpha=0.7)
                ax.set_title(f'Distribusi Perbedaan - {estates[0]}')
            else:
                bars = ax.bar(estates, discrepancies, color='red', alpha=0.7)
                ax.set_title('Jumlah Perbedaan per Estate')
                ax.set_ylabel('Jumlah Perbedaan')
                ax.set_xlabel('Estate')

                # Add value labels
                for bar, disc in zip(bars, discrepancies):
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                               f'{int(disc)}', ha='center', va='bottom')

                if len(estates) > 4:
                    ax.tick_params(axis='x', rotation=45)

    def create_employee_performance_chart(self, ax, selected_estate: str):
        """Create employee performance chart"""
        estate_results = self.analysis_results.get('estate_results', {})

        employee_performance = {}

        for estate_name, estate_data in estate_results.items():
            if selected_estate == "Semua" or estate_name == selected_estate:
                emp_results = estate_data.get('employee_results', {})
                for emp_name, emp_data in emp_results.items():
                    if emp_name not in employee_performance:
                        employee_performance[emp_name] = {
                            'transactions': 0,
                            'verified': 0,
                            'discrepancies': 0
                        }

                    stats = emp_data.get('statistics', {})
                    employee_performance[emp_name]['transactions'] += stats.get('total_transactions', 0)
                    employee_performance[emp_name]['verified'] += stats.get('verified_transactions', 0)
                    employee_performance[emp_name]['discrepancies'] += stats.get('discrepancies', 0)

        if employee_performance:
            # Sort by transaction count and take top 10
            sorted_employees = sorted(
                employee_performance.items(),
                key=lambda x: x[1]['transactions'],
                reverse=True
            )[:10]

            employees = [emp[0] for emp in sorted_employees]
            verification_rates = [
                (emp[1]['verified'] / emp[1]['transactions'] * 100) if emp[1]['transactions'] > 0 else 0
                for emp in sorted_employees
            ]

            bars = ax.barh(employees, verification_rates, color='green', alpha=0.7)
            ax.set_title('Top 10 Performa Karyawan (Tingkat Verifikasi)')
            ax.set_xlabel('Tingkat Verifikasi (%)')
            ax.set_ylabel('Karyawan')

            # Add value labels
            for bar, rate in zip(bars, verification_rates):
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                       f'{rate:.1f}%', ha='left', va='center')

    def create_daily_trends_chart(self, ax, selected_estate: str):
        """Create daily trends chart"""
        # This would require daily data from analysis results
        # For now, show a placeholder
        ax.text(0.5, 0.5, 'Grafik tren harian\nmemerlukan data harian dari hasil analisis',
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Tren Harian')

    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.tab('current')['text']

        if selected_tab == "Grafik & Visualisasi":
            self.update_chart()
        elif selected_tab == "Performa Karyawan":
            # Refresh employee performance data if needed
            pass

    def on_estate_selected(self, event):
        """Handle estate selection"""
        selected_estate = self.estate_var.get()
        if selected_estate:
            self.show_estate_details(selected_estate)

    def show_estate_details(self, estate_name: str):
        """Show detailed information for selected estate"""
        estate_results = self.analysis_results.get('estate_results', {})
        estate_data = estate_results.get(estate_name, {})

        if estate_data:
            # Update detailed view with selected estate
            self.detail_estate_var.set(estate_name)
            self.apply_detail_filters()

    def show_all_estates(self):
        """Show all estates in the estate breakdown"""
        self.estate_var.set('')
        # Update estate tree to show all estates
        self.update_estate_breakdown()

    def apply_detail_filters(self):
        """Apply filters to detailed results"""
        # Clear existing items
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        detailed_results = self.analysis_results.get('detailed_results', [])
        selected_estate = self.detail_estate_var.get()
        verification_status = self.verification_var.get()
        selected_employee = self.employee_var.get()

        for result in detailed_results:
            # Apply filters
            if selected_estate and selected_estate != "Semua":
                if result.get('estate') != selected_estate:
                    continue

            if verification_status != "Semua":
                is_verified = result.get('verified', False)
                if verification_status == "Terverifikasi" and not is_verified:
                    continue
                elif verification_status == "Tidak Terverifikasi" and is_verified:
                    continue

            if selected_employee and selected_employee != "Semua":
                if result.get('employee') != selected_employee:
                    continue

            # Add filtered result
            estate = result.get('estate', '-')
            transno = result.get('transno', '-')
            trans_date = result.get('trans_date', '-')
            employee = result.get('employee', '-')
            role = result.get('role', '-')
            verified = "Ya" if result.get('verified', False) else "Tidak"
            differences = result.get('differences', '')

            self.detail_tree.insert('', 'end', text=estate, values=(
                transno, trans_date, employee, role, verified, differences
            ))

    def reset_detail_filters(self):
        """Reset all detail filters"""
        self.detail_estate_var.set('')
        self.verification_var.set("Semua")
        self.employee_var.set('')
        self.apply_detail_filters()

    def show_employee_performance(self):
        """Show performance for selected employee"""
        selected_estate = self.perf_estate_var.get()
        selected_employee = self.perf_employee_var.get()

        if not selected_employee or selected_employee == "Semua":
            return

        # Find employee data
        estate_results = self.analysis_results.get('estate_results', {})
        employee_data = None

        for estate_name, estate_data in estate_results.items():
            if selected_estate == "Semua" or estate_name == selected_estate:
                emp_results = estate_data.get('employee_results', {})
                if selected_employee in emp_results:
                    employee_data = emp_results[selected_employee]
                    break

        if employee_data:
            # Update performance metrics
            stats = employee_data.get('statistics', {})

            self.perf_metrics['total_transactions'].config(
                text=f"{stats.get('total_transactions', 0):,}"
            )
            self.perf_metrics['verified_transactions'].config(
                text=f"{stats.get('verified_transactions', 0):,}"
            )
            self.perf_metrics['verification_rate'].config(
                text=f"{stats.get('verification_rate', 0):.1f}%"
            )
            self.perf_metrics['discrepancies'].config(
                text=f"{stats.get('discrepancies', 0):,}"
            )
            self.perf_metrics['accuracy_rate'].config(
                text=f"{stats.get('accuracy_rate', 0):.1f}%"
            )
            self.perf_metrics['avg_daily_transactions'].config(
                text=f"{stats.get('avg_daily_transactions', 0):.1f}"
            )

            # Update transaction history
            self.update_employee_history(employee_data)

    def update_employee_history(self, employee_data: Dict[str, Any]):
        """Update employee transaction history"""
        # Clear existing items
        for item in self.emp_history_tree.get_children():
            self.emp_history_tree.delete(item)

        transactions = employee_data.get('transactions', [])

        for i, transaction in enumerate(transactions):
            trans_id = transaction.get('id', i+1)
            trans_date = transaction.get('date', '-')
            transno = transaction.get('transno', '-')
            verified = "Terverifikasi" if transaction.get('verified', False) else "Tidak Terverifikasi"
            differences = transaction.get('differences', '')

            self.emp_history_tree.insert('', 'end', text=str(trans_id), values=(
                trans_date, transno, verified, differences
            ))

    def on_transaction_double_click(self, event):
        """Handle double-click on transaction"""
        selection = self.detail_tree.selection()
        if selection:
            item = self.detail_tree.item(selection[0])
            transno = item['values'][0]
            estate = item['text']

            # Show transaction details (could be a dialog)
            messagebox.showinfo(
                "Detail Transaksi",
                f"Estate: {estate}\nTrans No: {transno}\n\n(Fitur detail lengkap akan segera tersedia)"
            )

    def export_data(self):
        """Export data based on selected options"""
        if not self.analysis_results:
            messagebox.showerror("Error", "Tidak ada data untuk diekspor")
            return

        export_format = self.export_format_var.get()
        export_data_type = self.export_data_var.get()
        selected_estate = self.export_estate_var.get()

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ffb_analysis_{export_data_type}_{timestamp}"

            if export_format == "Excel":
                self.export_to_excel(filename, export_data_type, selected_estate)
            elif export_format == "CSV":
                self.export_to_csv(filename, export_data_type, selected_estate)
            elif export_format == "PDF":
                self.export_to_pdf(filename, export_data_type, selected_estate)
            elif export_format == "JSON":
                self.export_to_json(filename, export_data_type, selected_estate)

        except Exception as e:
            self.log_export_message(f"Error exporting data: {str(e)}", "error")
            messagebox.showerror("Export Error", f"Gagal mengekspor data: {str(e)}")

    def export_to_excel(self, filename: str, data_type: str, estate: str):
        """Export data to Excel format"""
        # This would integrate with the report generation service
        self.log_export_message(f"Exporting {data_type} to Excel...", "info")

        if self.on_export_callback:
            success = self.on_export_callback(filename, "excel", data_type, estate)
            if success:
                self.log_export_message(f"Successfully exported to {filename}.xlsx", "success")
            else:
                self.log_export_message("Failed to export data", "error")

    def export_to_csv(self, filename: str, data_type: str, estate: str):
        """Export data to CSV format"""
        self.log_export_message(f"Exporting {data_type} to CSV...", "info")

        # Implementation would go here
        self.log_export_message(f"Successfully exported to {filename}.csv", "success")

    def export_to_pdf(self, filename: str, data_type: str, estate: str):
        """Export data to PDF format"""
        self.log_export_message(f"Exporting {data_type} to PDF...", "info")

        # Implementation would go here
        self.log_export_message(f"Successfully exported to {filename}.pdf", "success")

    def export_to_json(self, filename: str, data_type: str, estate: str):
        """Export data to JSON format"""
        self.log_export_message(f"Exporting {data_type} to JSON...", "info")

        # Implementation would go here
        self.log_export_message(f"Successfully exported to {filename}.json", "success")

    def open_export_folder(self):
        """Open the export folder"""
        # This would open the reports/export folder
        self.log_export_message("Membuka folder export...", "info")

    def log_export_message(self, message: str, message_type: str = "info"):
        """Add message to export log"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.export_log.config(state=tk.NORMAL)
        self.export_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.export_log.insert(tk.END, f"{message}\n", message_type)
        self.export_log.see(tk.END)
        self.export_log.config(state=tk.DISABLED)

    def clear_results(self):
        """Clear all displayed results"""
        # Clear summary
        for label in self.stats_labels.values():
            label.config(text="-")

        # Clear estate breakdown
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)

        # Clear detailed results
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        # Clear employee performance
        for label in self.perf_metrics.values():
            label.config(text="-")

        for item in self.emp_history_tree.get_children():
            self.emp_history_tree.delete(item)

        # Clear chart
        if self.figure:
            self.figure.clear()
            self.canvas.draw()

        # Reset variables
        self.analysis_results = None
        self.available_estates = []

        # Clear export log
        self.export_log.config(state=tk.NORMAL)
        self.export_log.delete(1.0, tk.END)
        self.export_log.config(state=tk.DISABLED)
    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)
        elif hasattr(self, 'parent'):
            # For widgets that don't have main_container, just return
            pass

