"""
GUI untuk Ifess Database Analysis Tool
Analisis kinerja karyawan FFB Scanner dengan interface grafis yang user-friendly
Enhanced version with comprehensive reporting capabilities
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from datetime import datetime, date, timedelta
import pandas as pd
from collections import defaultdict
import json
import calendar

# Import modul analisis yang sudah ada
from firebird_connector import FirebirdConnector

class IfessAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ifess Database Analysis Tool v3.0 - Enhanced")
        self.root.geometry("950x750")
        self.root.minsize(900, 700)
        
        # Variables
        self.db_path_var = tk.StringVar(value="C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB")
        self.isql_path_var = tk.StringVar(value="Auto-detect")
        self.month_var = tk.StringVar(value="05")
        self.year_var = tk.StringVar(value="2025")
        self.division_filter_var = tk.StringVar(value="All Divisions")
        self.analysis_type_var = tk.StringVar(value="Employee Performance")
        
        # Analysis data - Enhanced to match standalone script
        self.connector = None
        self.verification_stats = {}
        self.role_summary = {}
        self.division_summary = {}
        self.employee_mapping = {}
        self.transstatus_mapping = {}
        self.division_mapping = {}
        self.is_analyzing = False
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Setup user interface."""
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configuration Tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.setup_config_tab(config_frame)
        
        # Analysis Tab
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        self.setup_analysis_tab(analysis_frame)
        
        # Results Tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        self.setup_results_tab(results_frame)
        
        # Reports Tab - Enhanced
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Reports")
        self.setup_reports_tab(reports_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_config_tab(self, parent):
        """Setup configuration tab."""
        # Database Configuration
        db_frame = ttk.LabelFrame(parent, text="Database Configuration", padding=10)
        db_frame.pack(fill='x', padx=10, pady=5)
        
        # Database path
        ttk.Label(db_frame, text="Database Path:").grid(row=0, column=0, sticky='w', pady=2)
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=60)
        db_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(db_frame, text="Browse", command=self.browse_database).grid(row=0, column=2, padx=5, pady=2)
        
        # ISQL path
        ttk.Label(db_frame, text="ISQL Path:").grid(row=1, column=0, sticky='w', pady=2)
        isql_entry = ttk.Entry(db_frame, textvariable=self.isql_path_var, width=60)
        isql_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(db_frame, text="Browse", command=self.browse_isql).grid(row=1, column=2, padx=5, pady=2)
        
        db_frame.columnconfigure(1, weight=1)
        
        # Analysis Configuration
        analysis_frame = ttk.LabelFrame(parent, text="Analysis Configuration", padding=10)
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        # Month and Year
        period_frame = ttk.Frame(analysis_frame)
        period_frame.pack(fill='x', pady=5)
        
        ttk.Label(period_frame, text="Analysis Period:").pack(side='left')
        
        # Month selection
        ttk.Label(period_frame, text="Month:").pack(side='left', padx=(20, 5))
        month_combo = ttk.Combobox(period_frame, textvariable=self.month_var, width=10, state='readonly')
        month_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
        month_combo.pack(side='left', padx=5)
        
        # Year selection
        ttk.Label(period_frame, text="Year:").pack(side='left', padx=(20, 5))
        year_combo = ttk.Combobox(period_frame, textvariable=self.year_var, width=10, state='readonly')
        current_year = datetime.now().year
        year_combo['values'] = [str(y) for y in range(current_year-2, current_year+3)]
        year_combo.pack(side='left', padx=5)
        
        # Analysis Type
        type_frame = ttk.Frame(analysis_frame)
        type_frame.pack(fill='x', pady=5)
        
        ttk.Label(type_frame, text="Analysis Type:").pack(side='left')
        type_combo = ttk.Combobox(type_frame, textvariable=self.analysis_type_var, width=25, state='readonly')
        type_combo['values'] = ["Employee Performance", "Division Summary", "Transaction Analysis", "Verification Status"]
        type_combo.pack(side='left', padx=(20, 5))
        
        # Division Filter
        division_frame = ttk.Frame(analysis_frame)
        division_frame.pack(fill='x', pady=5)
        
        ttk.Label(division_frame, text="Division Filter:").pack(side='left')
        self.division_combo = ttk.Combobox(division_frame, textvariable=self.division_filter_var, width=25, state='readonly')
        self.division_combo['values'] = ["All Divisions"]
        self.division_combo.pack(side='left', padx=(20, 5))
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Divisions", command=self.load_divisions).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Config", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Config", command=self.load_config).pack(side='left', padx=5)
        
    def setup_analysis_tab(self, parent):
        """Setup analysis tab."""
        # Control frame
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Analysis buttons
        self.analyze_btn = ttk.Button(control_frame, text="Run Analysis", command=self.run_analysis, state='normal')
        self.analyze_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Analysis", command=self.stop_analysis, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Clear Results", command=self.clear_results).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export Results", command=self.export_results).pack(side='left', padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side='left')
        self.progress_var = tk.StringVar(value="Ready to analyze")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(side='left', padx=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(side='right', fill='x', expand=True, padx=10)
        
        # Log frame
        log_frame = ttk.LabelFrame(parent, text="Analysis Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill='both', expand=True)
        
    def setup_results_tab(self, parent):
        """Setup results tab."""
        # Results summary frame
        summary_frame = ttk.LabelFrame(parent, text="Analysis Summary", padding=5)
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=6, width=80, state='disabled')
        self.summary_text.pack(fill='x')
        
        # Results details frame
        details_frame = ttk.LabelFrame(parent, text="Detailed Results", padding=5)
        details_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for results
        columns = ('Employee', 'Role', 'Division', 'Total Transactions', 'Verified', 'Verification Rate')
        self.results_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor='center')
        
        # Scrollbars for treeview
        v_scroll = ttk.Scrollbar(details_frame, orient='vertical', command=self.results_tree.yview)
        h_scroll = ttk.Scrollbar(details_frame, orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack treeview and scrollbars
        self.results_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        
        # Results control frame
        results_control_frame = ttk.Frame(parent)
        results_control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(results_control_frame, text="Export Excel", command=self.export_excel).pack(side='left', padx=5)
        ttk.Button(results_control_frame, text="Export PDF", command=self.export_pdf).pack(side='left', padx=5)
        ttk.Button(results_control_frame, text="Generate Charts", command=self.generate_charts).pack(side='left', padx=5)
        
    def setup_reports_tab(self, parent):
        """Setup reports tab - Enhanced with comprehensive reporting."""
        # Reports instruction frame
        instruction_frame = ttk.LabelFrame(parent, text="Enhanced Reporting System", padding=10)
        instruction_frame.pack(fill='x', padx=10, pady=5)
        
        instruction_text = """
Enhanced Reporting Features:
• 4-Sheet Excel Report: Comprehensive analysis with Detail Karyawan, Summary Role, Summary Divisi, and Breakdown Status
• Comprehensive PDF Report: Professional report with executive summary, role analysis, and top performers
• Visualization Charts: Advanced 2x3 chart layout with role/division analysis and performance metrics
        """
        ttk.Label(instruction_frame, text=instruction_text, justify='left').pack(anchor='w')
        
        # Reports control frame
        reports_control_frame = ttk.Frame(parent)
        reports_control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(reports_control_frame, text="Generate 4-Sheet Excel Report", 
                  command=self.generate_4_sheet_excel_report, width=25).pack(side='left', padx=5)
        ttk.Button(reports_control_frame, text="Generate Comprehensive PDF Report", 
                  command=self.export_pdf, width=25).pack(side='left', padx=5)
        ttk.Button(reports_control_frame, text="Generate Visualization Charts", 
                  command=self.generate_visualization_charts, width=25).pack(side='left', padx=5)
        
        # Reports status frame
        status_frame = ttk.LabelFrame(parent, text="Report Status", padding=10)
        status_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.reports_status_text = scrolledtext.ScrolledText(status_frame, height=15, width=80)
        self.reports_status_text.pack(fill='both', expand=True)
        
        # Add initial status message
        initial_msg = """Report Generation Status:
Ready to generate comprehensive reports. Please run analysis first to generate data.

Report Features Summary:
✓ Enhanced employee performance analysis with dual verification logic
✓ RECORDTAG-based role determination (PM=KERANI, P1=ASISTEN, P5=MANDOR)
✓ Status code 704 recognition as VERIFIED
✓ Multiple record verification detection
✓ Comprehensive division integration
✓ Advanced visualization with 2x3 chart layout
✓ Professional PDF reports with executive summary

Status: Waiting for analysis data...
"""
        self.reports_status_text.insert(tk.END, initial_msg)
        
    def browse_database(self):
        """Browse for database file."""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)
            
    def browse_isql(self):
        """Browse for ISQL executable."""
        filename = filedialog.askopenfilename(
            title="Select ISQL Executable",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if filename:
            self.isql_path_var.set(filename)
            
    def log_message(self, message):
        """Add message to log and reports status."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Also log to reports status if it exists
        if hasattr(self, 'reports_status_text'):
            self.reports_status_text.insert(tk.END, log_entry)
            self.reports_status_text.see(tk.END)
        
        self.root.update_idletasks()
        
    def update_status(self, status):
        """Update status bar."""
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def test_connection(self):
        """Test database connection."""
        try:
            self.update_status("Testing connection...")
            self.log_message("Testing database connection...")
            
            db_path = self.db_path_var.get()
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
                
            # Setup ISQL path
            isql_path = self.isql_path_var.get()
            if isql_path == "Auto-detect":
                connector = FirebirdConnector(db_path)
            else:
                connector = FirebirdConnector(db_path, isql_path=isql_path)
                
            if connector.test_connection():
                self.connector = connector
                self.log_message("✓ Database connection successful!")
                messagebox.showinfo("Success", "Database connection successful!")
                self.update_status("Connected")
            else:
                self.log_message("✗ Database connection failed!")
                messagebox.showerror("Error", "Database connection failed!")
                self.update_status("Connection failed")
                
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            self.update_status("Connection error")
            
    def load_divisions(self):
        """Load division data from database."""
        if not self.connector:
            messagebox.showwarning("Warning", "Please test connection first!")
            return
            
        try:
            self.update_status("Loading divisions...")
            self.log_message("Loading division data...")
            
            # Query untuk mendapatkan data division
            division_query = """
            SELECT a.ID, a.OCID, a.DIVCODE, a.DIVNAME
            FROM CRDIVISION a
            ORDER BY a.DIVNAME
            """
            
            result = self.connector.execute_query(division_query)
            df = self.connector.to_pandas(result)
            
            if not df.empty:
                self.division_data = {}
                division_names = ["All Divisions"]
                
                for _, row in df.iterrows():
                    div_id = str(row.iloc[0]) if len(row) > 0 else ''
                    div_name = str(row.iloc[3]) if len(row) > 3 else f"Division-{div_id}"
                    
                    self.division_data[div_id] = div_name
                    division_names.append(div_name)
                
                # Update division combobox
                self.division_combo['values'] = division_names
                
                self.log_message(f"✓ Loaded {len(self.division_data)} divisions")
                messagebox.showinfo("Success", f"Loaded {len(self.division_data)} divisions")
                self.update_status("Divisions loaded")
            else:
                self.log_message("⚠ No division data found")
                messagebox.showwarning("Warning", "No division data found")
                
        except Exception as e:
            error_msg = f"Error loading divisions: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
    def get_division_enhanced_data(self):
        """Get transaction data with division information."""
        month = int(self.month_var.get())
        year = int(self.year_var.get())
        table_name = f"FFBSCANNERDATA{month:02d}"
        
        # Calculate proper date range
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate end date (first day of next month)
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        # Main query dengan join untuk mendapatkan division data
        query = f"""
        SELECT 
            a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
            a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
            a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
            a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
            a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2,
            b.DIVID, c.DIVNAME
        FROM {table_name} a
        LEFT JOIN OCFIELD b ON a.FIELDID = b.ID AND a.OCID = b.OCID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID AND b.OCID = c.OCID
        WHERE a.TRANSDATE >= '{start_date}' 
        AND a.TRANSDATE < '{end_date}'
        ORDER BY a.TRANSNO, a.TRANSDATE, a.TRANSTIME
        """
        
        self.log_message(f"Executing query for {table_name}...")
        self.log_message(f"Date range: {start_date} to {end_date}")
        result = self.connector.execute_query(query)
        df = self.connector.to_pandas(result)
        
        return df
        
    def analyze_employee_performance_with_divisions(self, df):
        """Analyze employee performance with division data."""
        if df.empty:
            return {}, {}
            
        self.log_message("Analyzing employee performance with divisions...")
        
        # Get employee mapping
        employee_mapping = self.get_employee_mapping()
        
        # Analisis per karyawan dengan division
        employee_stats = defaultdict(lambda: {
            'total_created': 0,
            'total_verified': 0,
            'verification_rate': 0,
            'division': 'Unknown',
            'role': 'Unknown',
            'transactions': set()
        })
        
        # Process each transaction
        for _, row in df.iterrows():
            try:
                creator_id = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''  # SCANUSERID
                status = str(row.iloc[19]).strip() if pd.notna(row.iloc[19]) else '0'    # TRANSSTATUS
                transno = str(row.iloc[14]).strip() if pd.notna(row.iloc[14]) else ''    # TRANSNO
                division = str(row.iloc[-1]).strip() if pd.notna(row.iloc[-1]) else 'Unknown'  # DIVNAME
                
                if creator_id:
                    creator_name = employee_mapping.get(creator_id, f"Employee-{creator_id}")
                    
                    employee_stats[creator_name]['total_created'] += 1
                    employee_stats[creator_name]['transactions'].add(transno)
                    employee_stats[creator_name]['division'] = division
                    employee_stats[creator_name]['role'] = self.get_employee_role(creator_name)
                    
                    # Count verified transactions
                    if status in ['1', 'Verified']:
                        employee_stats[creator_name]['total_verified'] += 1
                        
            except Exception as e:
                self.log_message(f"Error processing row: {e}")
                continue
        
        # Calculate verification rates
        verification_stats = {}
        for emp_name, stats in employee_stats.items():
            verification_rate = 0
            if stats['total_created'] > 0:
                verification_rate = (stats['total_verified'] / stats['total_created']) * 100
                
            verification_stats[emp_name] = {
                'employee_name': emp_name,
                'role': stats['role'],
                'division': stats['division'],
                'total_created': stats['total_created'],
                'total_verified': stats['total_verified'],
                'verification_rate': verification_rate,
                'unique_transactions': len(stats['transactions'])
            }
        
        return verification_stats, employee_stats
        
    def get_employee_mapping(self):
        """Get employee ID to name mapping - Enhanced version."""
        try:
            query = "SELECT ID, NAME FROM EMP"
            result = self.connector.execute_query(query)
            df = self.connector.to_pandas(result)
            
            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    emp_id = str(row.iloc[0]).strip()
                    emp_name = str(row.iloc[1]).strip()
                    if emp_id and emp_name:
                        mapping[emp_id] = emp_name
                        
            # Create get_name function for compatibility
            def get_employee_name(emp_id):
                return mapping.get(str(emp_id).strip(), f"KARYAWAN-{emp_id}")
            
            enhanced_mapping = mapping.copy()
            enhanced_mapping['get_name'] = get_employee_name
            
            self.log_message(f"✓ Employee mapping loaded: {len(mapping)} employees")
            return enhanced_mapping
            
        except Exception as e:
            self.log_message(f"✗ Error getting employee mapping: {e}")
            return {'get_name': lambda emp_id: f"KARYAWAN-{emp_id}"}

    def get_transstatus_mapping(self):
        """Get transaction status mapping - Enhanced version."""
        try:
            query = "SELECT ID, SHORTCODE, NAME FROM LOOKUP"
            result = self.connector.execute_query(query)
            df = self.connector.to_pandas(result)
            
            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    status_id = str(row.iloc[0]).strip()
                    status_name = str(row.iloc[2]).strip()
                    if status_id and status_name:
                        mapping[status_id] = status_name
            
            # Create get_status_name function for compatibility
            def get_status_name(status_id):
                return mapping.get(str(status_id).strip(), f"STATUS-{status_id}")
            
            enhanced_mapping = mapping.copy()
            enhanced_mapping['get_status_name'] = get_status_name
            
            self.log_message(f"✓ Status mapping loaded: {len(mapping)} statuses")
            return enhanced_mapping
            
        except Exception as e:
            self.log_message(f"✗ Error getting status mapping: {e}")
            return {'get_status_name': lambda status_id: f"STATUS-{status_id}"}

    def get_division_mapping(self):
        """Get division mapping - Enhanced version."""
        try:
            query = "SELECT ID, DIVCODE, DIVNAME FROM CRDIVISION ORDER BY DIVNAME"
            result = self.connector.execute_query(query)
            df = self.connector.to_pandas(result)
            
            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    div_id = str(row.iloc[0]).strip()
                    div_name = str(row.iloc[2]).strip()
                    if div_id and div_name:
                        mapping[div_id] = div_name
            
            # Create get_division_name function for compatibility
            def get_division_name(div_id):
                return mapping.get(str(div_id).strip(), f"DIVISION-{div_id}")
            
            enhanced_mapping = mapping.copy()
            enhanced_mapping['get_division_name'] = get_division_name
            
            self.log_message(f"✓ Division mapping loaded: {len(mapping)} divisions")
            return enhanced_mapping
            
        except Exception as e:
            self.log_message(f"✗ Error getting division mapping: {e}")
            return {'get_division_name': lambda div_id: f"DIVISION-{div_id}"}

    def get_employee_role_from_recordtag(self, recordtag):
        """Determine employee role from RECORDTAG - Enhanced version."""
        if not recordtag:
            return 'LAINNYA'
        
        recordtag_str = str(recordtag).strip().upper()
        
        # Mapping berdasarkan RECORDTAG seperti di analisis_per_karyawan.py
        role_mapping = {
            'PM': 'KERANI',    # Plantation Manager/Kerani
            'P1': 'ASISTEN',   # Asisten
            'P5': 'MANDOR',    # Mandor
        }
        
        return role_mapping.get(recordtag_str, 'LAINNYA')
            
    def get_employee_role(self, employee_name):
        """Determine employee role from name - Enhanced version."""
        if not employee_name:
            return 'LAINNYA'
        
        name_upper = employee_name.upper()
        if 'KERANI' in name_upper:
            return 'KERANI'
        elif 'ASISTEN' in name_upper:
            return 'ASISTEN'
        elif 'MANDOR' in name_upper:
            return 'MANDOR'
        elif 'ADMIN' in name_upper:
            return 'ADMIN'
        else:
            return 'LAINNYA'
            
    def is_transaction_verified(self, status_code, status_mapping=None):
        """Determine if transaction is verified - Enhanced version."""
        if not status_code:
            return False
        
        status_str = str(status_code).strip()
        
        # Status codes yang dianggap sebagai "verified"
        verified_status_codes = {
            '1',     # Standard verified status
            '704',   # Status OK - dianggap sebagai VERIFIED berdasarkan LOOKUP table
        }
        
        # Cek berdasarkan status code langsung
        if status_str in verified_status_codes:
            return True
        
        # Cek berdasarkan nama status jika mapping tersedia
        if status_mapping and 'get_status_name' in status_mapping:
            status_name = status_mapping['get_status_name'](status_str).upper()
            verified_status_names = {'VERIFIED', 'APPROVED', 'CONFIRMED', 'VALID', 'OK'}
            if any(verified_name in status_name for verified_name in verified_status_names):
                return True
        
        return False

    def check_transaction_verification_by_duplicates(self, df, transno_col, transdate_col, transstatus_col):
        """Check verification by duplicate records - Enhanced version."""
        verified_transactions = set()
        
        # Group by TRANSNO dan TRANSDATE
        transaction_groups = defaultdict(list)
        
        for _, row in df.iterrows():
            try:
                transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
                transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
                transstatus = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else ''
                
                if transno and transdate:
                    transaction_groups[(transno, transdate)].append({
                        'transno': transno,
                        'transdate': transdate,
                        'transstatus': transstatus,
                        'row_index': row.name
                    })
            except Exception as e:
                continue
        
        # Identifikasi transaksi yang verified berdasarkan multiple records
        for (transno, transdate), records in transaction_groups.items():
            if len(records) > 1:
                has_verified_status = any(self.is_transaction_verified(record['transstatus'], self.transstatus_mapping) for record in records)
                if has_verified_status:
                    verified_transactions.add((transno, transdate))
        
        return verified_transactions

    def analyze_employee_performance_comprehensive(self, df):
        """Comprehensive employee performance analysis - Enhanced version."""
        if df.empty:
            self.log_message("✗ No data to analyze")
            return {}, {}
        
        self.log_message("Starting comprehensive employee performance analysis...")
        
        # Column mapping
        scanuserid_col = 1   # SCANUSERID
        recordtag_col = 18   # RECORDTAG
        transstatus_col = 19 # TRANSSTATUS
        transno_col = 14     # TRANSNO
        transdate_col = 15   # TRANSDATE
        divname_col = 29     # DIVNAME
        
        self.log_message(f"Using columns: SCANUSERID={scanuserid_col}, RECORDTAG={recordtag_col}, TRANSSTATUS={transstatus_col}")
        
        # Get verified transactions through duplicate detection
        verified_transactions = self.check_transaction_verification_by_duplicates(
            df, transno_col, transdate_col, transstatus_col)
        
        self.log_message(f"Found {len(verified_transactions)} verified transactions through duplicate detection")
        
        # Employee statistics
        employee_stats = defaultdict(lambda: {
            'total_created': 0,
            'total_verified': 0,
            'status_breakdown': defaultdict(int),
            'transactions_created': set(),
            'transactions_verified': set(),
            'role': 'UNKNOWN',
            'division': 'Unknown'
        })
        
        # Analyze all transactions
        for _, row in df.iterrows():
            try:
                creator_id = str(row.iloc[scanuserid_col]).strip() if pd.notna(row.iloc[scanuserid_col]) else ''
                recordtag = str(row.iloc[recordtag_col]).strip() if pd.notna(row.iloc[recordtag_col]) else ''
                status = str(row.iloc[transstatus_col]).strip() if pd.notna(row.iloc[transstatus_col]) else '0'
                transno = str(row.iloc[transno_col]).strip() if pd.notna(row.iloc[transno_col]) else ''
                transdate = str(row.iloc[transdate_col]).strip() if pd.notna(row.iloc[transdate_col]) else ''
                division = str(row.iloc[divname_col]).strip() if pd.notna(row.iloc[divname_col]) else 'Unknown'
                
                if creator_id:
                    # Get employee name
                    if 'get_name' in self.employee_mapping:
                        creator_name = self.employee_mapping['get_name'](creator_id)
                    else:
                        creator_name = self.employee_mapping.get(creator_id, f"KARYAWAN-{creator_id}")
                    
                    # Determine role using RECORDTAG as primary method
                    if recordtag and recordtag != '':
                        role = self.get_employee_role_from_recordtag(recordtag)
                    else:
                        # Fallback to name-based method
                        role = self.get_employee_role(creator_name)
                    
                    # Determine division
                    if not division or division == 'None' or division == 'nan':
                        division = 'UNKNOWN'
                    
                    # Update employee statistics
                    employee_stats[creator_name]['total_created'] += 1
                    employee_stats[creator_name]['transactions_created'].add((transno, transdate))
                    employee_stats[creator_name]['status_breakdown'][status] += 1
                    employee_stats[creator_name]['role'] = role
                    employee_stats[creator_name]['division'] = division
                    
                    # Check verification using dual methods
                    is_verified = False
                    
                    # Method 1: Status code verification
                    if self.is_transaction_verified(status, self.transstatus_mapping):
                        is_verified = True
                    
                    # Method 2: Multiple records verification
                    if (transno, transdate) in verified_transactions:
                        is_verified = True
                    
                    if is_verified:
                        employee_stats[creator_name]['total_verified'] += 1
                        employee_stats[creator_name]['transactions_verified'].add((transno, transdate))
                
            except Exception as e:
                self.log_message(f"Error processing row: {e}")
                continue
        
        # Convert to final format
        verification_stats = {}
        for emp_name, stats in employee_stats.items():
            verification_rate = 0
            if stats['total_created'] > 0:
                verification_rate = (stats['total_verified'] / stats['total_created']) * 100
            
            verification_stats[emp_name] = {
                'employee_name': emp_name,
                'role': stats['role'],
                'division': stats['division'],
                'total_created': stats['total_created'],
                'total_verified': stats['total_verified'],
                'verification_rate': verification_rate,
                'unique_transactions': len(stats['transactions_created']),
                'unique_verified_transactions': len(stats['transactions_verified']),
                'status_breakdown': dict(stats['status_breakdown'])
            }
        
        self.log_message(f"✓ Analysis completed for {len(verification_stats)} employees")
        
        return verification_stats, employee_stats

    def generate_summary_statistics(self, verification_stats):
        """Generate summary statistics by role and division - Enhanced version."""
        role_summary = defaultdict(lambda: {
            'employee_count': 0,
            'total_transactions_created': 0,
            'total_transactions_verified': 0,
            'avg_verification_rate': 0,
            'employees': []
        })
        
        division_summary = defaultdict(lambda: {
            'employee_count': 0,
            'total_transactions_created': 0,
            'total_transactions_verified': 0,
            'avg_verification_rate': 0,
            'employees': []
        })
        
        for emp_name, stats in verification_stats.items():
            role = stats['role']
            division = stats['division']
            
            # Summary per role
            role_summary[role]['employee_count'] += 1
            role_summary[role]['total_transactions_created'] += stats['total_created']
            role_summary[role]['total_transactions_verified'] += stats['total_verified']
            role_summary[role]['employees'].append(emp_name)
            
            # Summary per division
            division_summary[division]['employee_count'] += 1
            division_summary[division]['total_transactions_created'] += stats['total_created']
            division_summary[division]['total_transactions_verified'] += stats['total_verified']
            division_summary[division]['employees'].append(emp_name)
        
        # Calculate average verification rates
        for role in role_summary:
            employees_in_role = [verification_stats[emp] for emp in role_summary[role]['employees']]
            if employees_in_role:
                avg_rate = sum(emp['verification_rate'] for emp in employees_in_role) / len(employees_in_role)
                role_summary[role]['avg_verification_rate'] = avg_rate
        
        for division in division_summary:
            employees_in_division = [verification_stats[emp] for emp in division_summary[division]['employees']]
            if employees_in_division:
                avg_rate = sum(emp['verification_rate'] for emp in employees_in_division) / len(employees_in_division)
                division_summary[division]['avg_verification_rate'] = avg_rate
        
        return dict(role_summary), dict(division_summary)
            
    def run_analysis(self):
        """Run the analysis in a separate thread."""
        if self.is_analyzing:
            return
            
        if not self.connector:
            messagebox.showwarning("Warning", "Please test connection first!")
            return
            
        # Start analysis thread
        self.is_analyzing = True
        self.analyze_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress_bar.start()
        
        analysis_thread = threading.Thread(target=self._perform_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
    def _perform_analysis(self):
        """Perform the actual analysis - Enhanced version."""
        try:
            self.update_status("Running analysis...")
            self.progress_var.set("Loading mappings...")
            
            # Load all mappings first
            self.employee_mapping = self.get_employee_mapping()
            self.transstatus_mapping = self.get_transstatus_mapping()
            self.division_mapping = self.get_division_mapping()
            
            self.progress_var.set("Fetching data from database...")
            
            # Get enhanced data with divisions
            df = self.get_division_enhanced_data()
            
            if df.empty:
                self.log_message("✗ No data found for the selected period")
                messagebox.showwarning("Warning", "No data found for the selected period")
                return
                
            self.log_message(f"✓ Retrieved {len(df)} transaction records")
            
            self.progress_var.set("Analyzing employee performance...")
            
            # Perform comprehensive analysis
            verification_stats, employee_stats = self.analyze_employee_performance_comprehensive(df)
            
            if not verification_stats:
                self.log_message("✗ No analysis results generated")
                messagebox.showwarning("Warning", "No analysis results generated")
                return
                
            self.verification_stats = verification_stats
            
            # Generate summary statistics
            self.progress_var.set("Generating summary statistics...")
            role_summary, division_summary = self.generate_summary_statistics(verification_stats)
            self.role_summary = role_summary
            self.division_summary = division_summary
            
            # Update results on main thread
            self.root.after(0, self._update_results_display)
            
            self.log_message(f"✓ Analysis completed for {len(verification_stats)} employees")
            self.log_message(f"✓ Found {len(role_summary)} roles and {len(division_summary)} divisions")
            self.progress_var.set("Analysis completed successfully")
            
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            # Reset UI state
            self.is_analyzing = False
            self.root.after(0, self._reset_analysis_ui)
            
    def _update_results_display(self):
        """Update the results display."""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Apply division filter
        division_filter = self.division_filter_var.get()
        filtered_results = self.verification_stats
        
        if division_filter != "All Divisions":
            filtered_results = {
                name: stats for name, stats in self.verification_stats.items()
                if stats['division'] == division_filter
            }
            
        # Sort by verification rate
        sorted_results = sorted(filtered_results.items(), 
                              key=lambda x: x[1]['verification_rate'], reverse=True)
        
        # Insert results into treeview
        for emp_name, stats in sorted_results:
            self.results_tree.insert('', 'end', values=(
                emp_name,
                stats['role'],
                stats['division'],
                stats['total_created'],
                stats['total_verified'],
                f"{stats['verification_rate']:.1f}%"
            ))
            
        # Update summary
        self._update_summary_display(filtered_results)
        
    def _update_summary_display(self, results):
        """Update the summary display."""
        if not results:
            return
            
        total_employees = len(results)
        total_transactions = sum(stats['total_created'] for stats in results.values())
        total_verified = sum(stats['total_verified'] for stats in results.values())
        avg_verification_rate = sum(stats['verification_rate'] for stats in results.values()) / total_employees
        
        # Group by division
        division_summary = defaultdict(lambda: {'employees': 0, 'transactions': 0, 'verified': 0})
        for stats in results.values():
            div = stats['division']
            division_summary[div]['employees'] += 1
            division_summary[div]['transactions'] += stats['total_created']
            division_summary[div]['verified'] += stats['total_verified']
            
        # Update summary text
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)
        
        summary = f"""Analysis Summary:
• Total Employees: {total_employees}
• Total Transactions: {total_transactions}
• Total Verified: {total_verified}
• Average Verification Rate: {avg_verification_rate:.1f}%

Division Breakdown:"""
        
        for div, data in division_summary.items():
            rate = (data['verified'] / data['transactions']) * 100 if data['transactions'] > 0 else 0
            summary += f"\n• {div}: {data['employees']} employees, {data['transactions']} transactions ({rate:.1f}% verified)"
            
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state='disabled')
        
    def _reset_analysis_ui(self):
        """Reset analysis UI state."""
        self.analyze_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_bar.stop()
        self.update_status("Analysis completed")
        
    def stop_analysis(self):
        """Stop the analysis."""
        self.is_analyzing = False
        self.log_message("Analysis stopped by user")
        self.progress_var.set("Analysis stopped")
        self._reset_analysis_ui()
        
    def clear_results(self):
        """Clear all results."""
        self.verification_stats = {}
        self.role_summary = {}
        self.division_summary = {}
        self.employee_mapping = {}
        self.transstatus_mapping = {}
        self.division_mapping = {}
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.config(state='disabled')
        self.log_message("Results cleared")
        
    def export_results(self):
        """Export results to various formats."""
        if not self.verification_stats:
            messagebox.showwarning("Warning", "No results to export")
            return
            
        # Show export options dialog
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Options")
        export_window.geometry("300x200")
        export_window.transient(self.root)
        export_window.grab_set()
        
        ttk.Label(export_window, text="Select export format:").pack(pady=10)
        
        ttk.Button(export_window, text="Export to Excel", 
                  command=lambda: [self.export_excel(), export_window.destroy()]).pack(pady=5)
        ttk.Button(export_window, text="Export to PDF", 
                  command=lambda: [self.export_pdf(), export_window.destroy()]).pack(pady=5)
        ttk.Button(export_window, text="Export to CSV", 
                  command=lambda: [self.export_csv(), export_window.destroy()]).pack(pady=5)
        ttk.Button(export_window, text="Cancel", 
                  command=export_window.destroy).pack(pady=10)
                  
    def export_excel(self):
        """Export results to Excel."""
        if not self.verification_stats:
            messagebox.showwarning("Warning", "No results to export")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Excel Report"
            )
            
            if filename:
                # Create DataFrame
                data = []
                for emp_name, stats in self.verification_stats.items():
                    data.append({
                        'Employee Name': emp_name,
                        'Role': stats['role'],
                        'Division': stats['division'],
                        'Total Transactions': stats['total_created'],
                        'Verified Transactions': stats['total_verified'],
                        'Verification Rate (%)': round(stats['verification_rate'], 2),
                        'Unique Transactions': stats['unique_transactions']
                    })
                
                df = pd.DataFrame(data)
                df.to_excel(filename, index=False)
                
                self.log_message(f"✓ Results exported to {filename}")
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
        except Exception as e:
            error_msg = f"Error exporting to Excel: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
    def export_pdf(self):
        """Export results to PDF."""
        if not self.verification_stats:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Save Comprehensive PDF Report"
            )
            
            if filename:
                self.log_message("Generating comprehensive PDF report...")
                
                # Import required modules
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib import colors
                from reportlab.lib.units import inch
                
                doc = SimpleDocTemplate(filename, pagesize=A4)
                styles = getSampleStyleSheet()
                story = []
                
                # Title
                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                           fontSize=16, spaceAfter=30, alignment=1)
                story.append(Paragraph("LAPORAN ANALISIS KINERJA KARYAWAN FFB Scanner", title_style))
                story.append(Paragraph(f"Tanggal Analisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
                story.append(Paragraph(f"Periode: {self.month_var.get()}/{self.year_var.get()}", styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Summary
                story.append(Paragraph("RINGKASAN EKSEKUTIF", styles['Heading2']))
                summary_text = f"""
                Total Karyawan Dianalisis: {len(self.verification_stats)}<br/>
                Total Role: {len(self.role_summary)}<br/>
                Total Divisi: {len(self.division_summary)}<br/>
                """
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Role Summary
                if self.role_summary:
                    story.append(Paragraph("SUMMARY PER ROLE", styles['Heading2']))
                    role_data = [['Role', 'Jumlah Karyawan', 'Rata-rata Verifikasi (%)']]
                    for role, stats in self.role_summary.items():
                        role_data.append([
                            role,
                            str(stats['employee_count']),
                            f"{stats['avg_verification_rate']:.1f}%"
                        ])
                    
                    role_table = Table(role_data)
                    role_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(role_table)
                    story.append(Spacer(1, 20))
                
                # Top Performers
                story.append(Paragraph("TOP 10 KARYAWAN - TINGKAT VERIFIKASI TERTINGGI", styles['Heading2']))
                top_performers = sorted(self.verification_stats.items(), 
                                      key=lambda x: x[1]['verification_rate'], reverse=True)[:10]
                
                top_data = [['No', 'Nama Karyawan', 'Role', 'Divisi', 'Tingkat Verifikasi (%)', 'Total Transaksi']]
                for i, (name, stats) in enumerate(top_performers, 1):
                    top_data.append([
                        str(i),
                        name[:25] + '...' if len(name) > 25 else name,
                        stats['role'],
                        stats['division'][:15] + '...' if len(stats['division']) > 15 else stats['division'],
                        f"{stats['verification_rate']:.1f}%",
                        str(stats['total_created'])
                    ])
                
                top_table = Table(top_data)
                top_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(top_table)
                
                doc.build(story)
                
                self.log_message(f"✓ Comprehensive PDF report saved: {filename}")
                messagebox.showinfo("Success", f"Comprehensive PDF report saved to:\n{filename}")
                
        except ImportError:
            error_msg = "ReportLab library not available for PDF generation"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Error generating PDF report: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
    def generate_visualization_charts(self):
        """Generate comprehensive visualization charts."""
        if not self.verification_stats:
            messagebox.showwarning("Warning", "No analysis results to visualize")
            return
            
        try:
            output_dir = filedialog.askdirectory(title="Select Output Directory for Charts")
            if not output_dir:
            return
            
            self.log_message("Generating comprehensive visualization charts...")
            
            # Import required modules
            import matplotlib.pyplot as plt
            import seaborn as sns
            import numpy as np
            
            # Set style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create 2x3 subplot layout
            fig, axes = plt.subplots(2, 3, figsize=(20, 12))
            fig.suptitle('Analisis Kinerja Karyawan FFB Scanner - Komprehensif', fontsize=16, fontweight='bold')
            
            # 1. Top employees by verification rate
            sorted_employees = sorted(self.verification_stats.items(), 
                                    key=lambda x: x[1]['total_created'], reverse=True)[:15]
            
            if sorted_employees:
                names = [emp[0][:20] + '...' if len(emp[0]) > 20 else emp[0] for emp, _ in sorted_employees]
                rates = [stats['verification_rate'] for _, stats in sorted_employees]
                colors_emp = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in rates]
                
                axes[0,0].barh(names, rates, color=colors_emp)
                axes[0,0].set_xlabel('Tingkat Verifikasi (%)')
                axes[0,0].set_title('Top 15 Karyawan - Tingkat Verifikasi')
                axes[0,0].grid(axis='x', alpha=0.3)
                
                for i, rate in enumerate(rates):
                    axes[0,0].text(rate + 1, i, f'{rate:.1f}%', va='center', fontsize=8)
            
            # 2. Total transactions by employee
            if sorted_employees:
                totals = [stats['total_created'] for _, stats in sorted_employees]
                
                axes[0,1].barh(names, totals, color='skyblue')
                axes[0,1].set_xlabel('Jumlah Transaksi Dibuat')
                axes[0,1].set_title('Top 15 Karyawan - Total Transaksi Dibuat')
                axes[0,1].grid(axis='x', alpha=0.3)
            
            # 3. Role distribution
            if self.role_summary:
                roles = list(self.role_summary.keys())
                role_counts = [self.role_summary[role]['employee_count'] for role in roles]
                
                axes[0,2].pie(role_counts, labels=roles, autopct='%1.1f%%', startangle=90)
                axes[0,2].set_title('Distribusi Karyawan per Role')
            
            # 4. Role verification rates
            if self.role_summary:
                role_rates = [self.role_summary[role]['avg_verification_rate'] for role in roles]
                colors_role = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in role_rates]
                
                axes[1,0].bar(roles, role_rates, color=colors_role)
                axes[1,0].set_ylabel('Rata-rata Tingkat Verifikasi (%)')
                axes[1,0].set_title('Tingkat Verifikasi per Role')
                axes[1,0].grid(axis='y', alpha=0.3)
                axes[1,0].set_ylim(0, 100)
                
                for i, rate in enumerate(role_rates):
                    axes[1,0].text(i, rate + 2, f'{rate:.1f}%', 
                                  ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # 5. Division distribution (top 10)
            if self.division_summary:
                sorted_divisions = sorted(self.division_summary.items(), 
                                        key=lambda x: x[1]['employee_count'], reverse=True)[:10]
                
                div_names = [div[:15] + '...' if len(div) > 15 else div for div, _ in sorted_divisions]
                div_counts = [stats['employee_count'] for _, stats in sorted_divisions]
                
                axes[1,1].bar(div_names, div_counts, color='lightcoral')
                axes[1,1].set_ylabel('Jumlah Karyawan')
                axes[1,1].set_title('Top 10 Divisi - Jumlah Karyawan')
                axes[1,1].grid(axis='y', alpha=0.3)
                axes[1,1].tick_params(axis='x', rotation=45)
            
            # 6. Division verification rates (top 10)
            if self.division_summary and sorted_divisions:
                div_rates = [stats['avg_verification_rate'] for _, stats in sorted_divisions]
                colors_div = ['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in div_rates]
                
                axes[1,2].bar(div_names, div_rates, color=colors_div)
                axes[1,2].set_ylabel('Rata-rata Tingkat Verifikasi (%)')
                axes[1,2].set_title('Top 10 Divisi - Tingkat Verifikasi')
                axes[1,2].grid(axis='y', alpha=0.3)
                axes[1,2].set_ylim(0, 100)
                axes[1,2].tick_params(axis='x', rotation=45)
                
                for i, rate in enumerate(div_rates):
                    axes[1,2].text(i, rate + 2, f'{rate:.1f}%', 
                                  ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_filename = f"analisis_karyawan_{timestamp}_comprehensive_charts.png"
            chart_path = os.path.join(output_dir, chart_filename)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            self.log_message(f"✓ Comprehensive charts saved: {chart_path}")
            messagebox.showinfo("Success", f"Comprehensive charts saved to:\n{chart_path}")
            
        except ImportError:
            error_msg = "Matplotlib/Seaborn libraries not available for chart generation"
                self.log_message(f"✗ {error_msg}")
                messagebox.showerror("Error", error_msg)
            except Exception as e:
            error_msg = f"Error generating charts: {str(e)}"
                self.log_message(f"✗ {error_msg}")
                messagebox.showerror("Error", error_msg)
                
    def generate_4_sheet_excel_report(self):
        """Generate comprehensive 4-sheet Excel report."""
        if not self.verification_stats:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Comprehensive Excel Report"
            )
            
            if filename:
                self.log_message("Generating comprehensive 4-sheet Excel report...")
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Sheet 1: Detail per karyawan
                    emp_data = []
                    for emp_name, stats in self.verification_stats.items():
                        emp_data.append({
                            'Nama Karyawan': emp_name,
                            'Role': stats['role'],
                            'Divisi': stats['division'],
                            'Total Transaksi Dibuat': stats['total_created'],
                            'Transaksi Unik Dibuat': stats['unique_transactions'],
                            'Total Verifikasi Dilakukan': stats['total_verified'],
                            'Transaksi Unik Verified': stats.get('unique_verified_transactions', 0),
                            'Tingkat Verifikasi (%)': round(stats['verification_rate'], 2)
                        })
                    
                    df_employees = pd.DataFrame(emp_data)
                    df_employees = df_employees.sort_values('Total Transaksi Dibuat', ascending=False)
                    df_employees.to_excel(writer, sheet_name='Detail Karyawan', index=False)
                    
                    # Sheet 2: Summary per role
                    role_data = []
                    for role, stats in self.role_summary.items():
                        role_data.append({
                            'Role': role,
                            'Jumlah Karyawan': stats['employee_count'],
                            'Total Transaksi Dibuat': stats['total_transactions_created'],
                            'Total Verifikasi Dilakukan': stats['total_transactions_verified'],
                            'Rata-rata Tingkat Verifikasi (%)': round(stats['avg_verification_rate'], 2)
                        })
                    
                    df_roles = pd.DataFrame(role_data)
                    df_roles.to_excel(writer, sheet_name='Summary Role', index=False)
                    
                    # Sheet 3: Summary per division
                    division_data = []
                    for division, stats in self.division_summary.items():
                        division_data.append({
                            'Divisi': division,
                            'Jumlah Karyawan': stats['employee_count'],
                            'Total Transaksi Dibuat': stats['total_transactions_created'],
                            'Total Verifikasi Dilakukan': stats['total_transactions_verified'],
                            'Rata-rata Tingkat Verifikasi (%)': round(stats['avg_verification_rate'], 2)
                        })
                    
                    df_divisions = pd.DataFrame(division_data)
                    df_divisions = df_divisions.sort_values('Jumlah Karyawan', ascending=False)
                    df_divisions.to_excel(writer, sheet_name='Summary Divisi', index=False)
                    
                    # Sheet 4: Status breakdown per karyawan
                    status_data = []
                    for emp_name, stats in self.verification_stats.items():
                        for status, count in stats['status_breakdown'].items():
                            status_data.append({
                                'Nama Karyawan': emp_name,
                                'Role': stats['role'],
                                'Divisi': stats['division'],
                                'Status': status,
                                'Jumlah': count
                            })
                    
                    if status_data:
                        df_status = pd.DataFrame(status_data)
                        df_status.to_excel(writer, sheet_name='Breakdown Status', index=False)
                
                self.log_message(f"✓ Comprehensive Excel report saved: {filename}")
                messagebox.showinfo("Success", f"Comprehensive report saved to:\n{filename}")
                
            except Exception as e:
            error_msg = f"Error generating Excel report: {str(e)}"
                self.log_message(f"✗ {error_msg}")
                messagebox.showerror("Error", error_msg)
        
    def export_csv(self):
        """Export results to CSV."""
        if not self.verification_stats:
            messagebox.showwarning("Warning", "No results to export")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save CSV Report"
            )
            
            if filename:
                # Create DataFrame
                data = []
                for emp_name, stats in self.verification_stats.items():
                    data.append({
                        'Employee Name': emp_name,
                        'Role': stats['role'],
                        'Division': stats['division'],
                        'Total Transactions': stats['total_created'],
                        'Verified Transactions': stats['total_verified'],
                        'Verification Rate (%)': round(stats['verification_rate'], 2),
                        'Unique Transactions': stats['unique_transactions']
                    })
                
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
                
                self.log_message(f"✓ Results exported to {filename}")
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
        except Exception as e:
            error_msg = f"Error exporting to CSV: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
        
    def save_config(self):
        """Save current configuration."""
        config = {
            'db_path': self.db_path_var.get(),
            'isql_path': self.isql_path_var.get(),
            'month': self.month_var.get(),
            'year': self.year_var.get(),
            'analysis_type': self.analysis_type_var.get(),
            'division_filter': self.division_filter_var.get()
        }
        
        try:
            with open('ifess_gui_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            self.log_message("✓ Configuration saved")
            messagebox.showinfo("Success", "Configuration saved successfully")
        except Exception as e:
            error_msg = f"Error saving configuration: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists('ifess_gui_config.json'):
                with open('ifess_gui_config.json', 'r') as f:
                    config = json.load(f)
                
                self.db_path_var.set(config.get('db_path', self.db_path_var.get()))
                self.isql_path_var.set(config.get('isql_path', self.isql_path_var.get()))
                self.month_var.set(config.get('month', self.month_var.get()))
                self.year_var.set(config.get('year', self.year_var.get()))
                self.analysis_type_var.set(config.get('analysis_type', self.analysis_type_var.get()))
                self.division_filter_var.set(config.get('division_filter', self.division_filter_var.get()))
                
                self.log_message("✓ Configuration loaded")
            else:
                self.log_message("No configuration file found, using defaults")
        except Exception as e:
            error_msg = f"Error loading configuration: {str(e)}"
            self.log_message(f"✗ {error_msg}")
            
def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = IfessAnalysisGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
    
if __name__ == "__main__":
    main() 