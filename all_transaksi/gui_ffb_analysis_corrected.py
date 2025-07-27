#!/usr/bin/env python3
"""
GUI Application untuk Analisis FFB Scanner Verification
Menggunakan logika yang benar dari create_correct_report.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
import os
from datetime import datetime, date
import threading
from firebird_connector import FirebirdConnector
from ffb_pdf_report_generator import generate_ffb_pdf_report

class FFBScannerAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisis Verifikasi FFB Scanner - Logika yang Benar")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Database configuration
        self.DB_PATH = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
        self.connector = None
        self.employee_mapping = {}
        
        # Analysis results
        self.analysis_results = []
        
        self.setup_ui()
        self.load_database()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Analisis Verifikasi FFB Scanner", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Database section
        db_frame = ttk.LabelFrame(main_frame, text="Konfigurasi Database", padding="10")
        db_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(db_frame, text="Path Database:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.db_path_var = tk.StringVar(value=self.DB_PATH)
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=60)
        db_entry.grid(row=0, column=1, padx=(10, 5), pady=5)
        
        ttk.Button(db_frame, text="Browse", command=self.browse_database).grid(row=0, column=2, pady=5)
        
        ttk.Button(db_frame, text="Test Koneksi", command=self.test_connection).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Date range section
        date_frame = ttk.LabelFrame(main_frame, text="Pemilihan Rentang Tanggal", padding="10")
        date_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(date_frame, text="Tanggal Mulai:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date = DateEntry(date_frame, width=20, background='darkblue', foreground='white', 
                                   borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(date_frame, text="Tanggal Akhir:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.end_date = DateEntry(date_frame, width=20, background='darkblue', foreground='white', 
                                 borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Set default dates (April 2025)
        self.start_date.set_date(date(2025, 4, 1))
        self.end_date.set_date(date(2025, 4, 28))
        
        # Division selection
        div_frame = ttk.LabelFrame(main_frame, text="Pemilihan Divisi (Otomatis)", padding="10")
        div_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(div_frame, text="Divisi yang tersedia di database:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Division listbox with scrollbar
        list_frame = ttk.Frame(div_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.division_listbox = tk.Listbox(list_frame, height=6, selectmode=tk.MULTIPLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.division_listbox.yview)
        self.division_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.division_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons for division selection
        btn_frame = ttk.Frame(div_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Pilih Semua", command=self.select_all_divisions).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hapus Pilihan", command=self.clear_division_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Divisi", command=self.refresh_divisions).pack(side=tk.LEFT, padx=5)
        
        # Analysis options
        options_frame = ttk.LabelFrame(main_frame, text="Opsi Analisis", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.generate_excel_var = tk.BooleanVar(value=True)
        self.generate_pdf_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Buat Laporan Excel", variable=self.generate_excel_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Buat Laporan PDF", variable=self.generate_pdf_var).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.progress_var = tk.StringVar(value="Siap untuk menganalisis")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Results text area
        results_frame = ttk.LabelFrame(main_frame, text="Hasil Analisis", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = tk.Text(text_frame, height=10, width=80)
        results_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Mulai Analisis", command=self.start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Hasil", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Buka Folder Output", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Keluar", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
    
    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.FDB"), ("All Files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)
            self.DB_PATH = filename
    
    def test_connection(self):
        """Test database connection"""
        try:
            self.progress_var.set("Menguji koneksi database...")
            self.progress_bar.start()
            
            connector = FirebirdConnector(self.db_path_var.get())
            if connector.test_connection():
                messagebox.showinfo("Berhasil", "Koneksi database berhasil!")
                self.connector = connector
                self.refresh_divisions()
            else:
                messagebox.showerror("Error", "Koneksi database gagal!")
        except Exception as e:
            messagebox.showerror("Error", f"Error koneksi: {str(e)}")
        finally:
            self.progress_bar.stop()
            self.progress_var.set("Siap untuk menganalisis")
    
    def load_database(self):
        """Load database and employee mapping"""
        try:
            self.connector = FirebirdConnector(self.DB_PATH)
            if self.connector.test_connection():
                self.employee_mapping = self.get_employee_name_mapping()
                self.refresh_divisions()
                self.log_message("Database berhasil dimuat")
            else:
                self.log_message("Gagal terhubung ke database")
        except Exception as e:
            self.log_message(f"Error memuat database: {str(e)}")
    
    def get_employee_name_mapping(self):
        """Get employee name mapping"""
        query = "SELECT ID, NAME FROM EMP"
        try:
            result = self.connector.execute_query(query)
            df = self.connector.to_pandas(result)
            
            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    emp_id = str(row.iloc[0]).strip()
                    emp_name = str(row.iloc[1]).strip()
                    mapping[emp_id] = emp_name
            
            return mapping
        except:
            return {}
    
    def refresh_divisions(self):
        """Refresh division list"""
        try:
            divisions = self.get_division_list()
            self.division_listbox.delete(0, tk.END)
            
            for div in divisions:
                self.division_listbox.insert(tk.END, f"{div['div_name']} (ID: {div['div_id']})")
            
            # Automatically select all divisions
            self.select_all_divisions()
            
            self.log_message(f"Memuat {len(divisions)} divisi dari database")
        except Exception as e:
            self.log_message(f"Error memuat divisi: {str(e)}")
    
    def get_division_list(self):
        """Get division list from FFBScanner table automatically"""
        # Query untuk mendapatkan divisi yang ada di FFBScanner
        query = """
        SELECT DISTINCT b.DIVID, c.DIVNAME, c.DIVCODE
        FROM FFBSCANNERDATA04 a
        JOIN OCFIELD b ON a.FIELDID = b.ID
        LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
        WHERE b.DIVID IS NOT NULL
        ORDER BY c.DIVNAME
        """
        
        try:
            result = self.connector.execute_query(query)
            df = self.connector.to_pandas(result)
            
            divisions = []
            if not df.empty:
                for _, row in df.iterrows():
                    div_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                    div_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                    
                    if div_id and div_name:
                        divisions.append({
                            'div_id': div_id,
                            'div_name': div_name
                        })
            
            return divisions
        except Exception as e:
            self.log_message(f"Error getting divisions: {str(e)}")
            return []
    
    def select_all_divisions(self):
        """Select all divisions"""
        self.division_listbox.selection_set(0, tk.END)
    
    def clear_division_selection(self):
        """Clear division selection"""
        self.division_listbox.selection_clear(0, tk.END)
    
    def start_analysis(self):
        """Start analysis in separate thread"""
        if not self.connector:
            messagebox.showerror("Error", "Silakan test koneksi database terlebih dahulu")
            return
        
        selected_indices = self.division_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Silakan pilih minimal satu divisi")
            return
        
        # Start analysis in separate thread
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
    
    def run_analysis(self):
        """Run the analysis"""
        try:
            self.progress_var.set("Memulai analisis...")
            self.progress_bar.start()
            
            # Get selected divisions
            selected_indices = self.division_listbox.curselection()
            divisions = self.get_division_list()
            selected_divisions = [divisions[i] for i in selected_indices]
            
            # Get date range
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            
            self.log_message(f"Menganalisis {len(selected_divisions)} divisi")
            self.log_message(f"Rentang tanggal: {start_date} sampai {end_date}")
            
            # Run analysis for each division
            self.analysis_results = []
            for i, div in enumerate(selected_divisions):
                self.progress_var.set(f"Menganalisis {div['div_name']} ({i+1}/{len(selected_divisions)})")
                
                result = self.analyze_division_correct(div['div_id'], div['div_name'], start_date, end_date)
                if result:
                    self.analysis_results.append(result)
                    self.log_message(f"✓ {div['div_name']}: {result['totals']['kerani']} KERANI, {result['totals']['verifications']} verifikasi")
            
            # Generate reports
            if self.analysis_results:
                self.generate_reports()
            
            self.progress_var.set("Analisis selesai")
            
        except Exception as e:
            self.log_message(f"Error analisis: {str(e)}")
            messagebox.showerror("Error", f"Analisis gagal: {str(e)}")
        finally:
            self.progress_bar.stop()
    
    def analyze_division_correct(self, div_id, div_name, start_date, end_date):
        """Analyze division dengan query yang benar"""
        # Format dates for SQL
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Determine month for table name
        month_num = start_date.month
        ffb_table = f"FFBSCANNERDATA{month_num:02d}"
        
        # Query untuk semua transaksi di divisi (TANPA filter status)
        query = f"""
        SELECT 
            a.SCANUSERID,
            a.RECORDTAG,
            COUNT(*) as transaction_count
        FROM 
            {ffb_table} a
        JOIN 
            OCFIELD b ON a.FIELDID = b.ID
        WHERE 
            b.DIVID = '{div_id}'
            AND a.TRANSDATE >= '{start_str}' 
            AND a.TRANSDATE < '{end_str}'
        GROUP BY a.SCANUSERID, a.RECORDTAG
        ORDER BY a.SCANUSERID, a.RECORDTAG
        """
        
        try:
            result = self.connector.execute_query(query)
            df = self.connector.to_pandas(result)
            
            if df.empty:
                return None
            
            # Process results
            employees = {}
            total_kerani = 0
            total_mandor = 0
            total_asisten = 0
            
            for _, row in df.iterrows():
                scanuserid = str(row.iloc[0]).strip()
                recordtag = str(row.iloc[1]).strip()
                count = int(row.iloc[2])
                
                emp_name = self.employee_mapping.get(scanuserid, f"EMPLOYEE-{scanuserid}")
                
                if scanuserid not in employees:
                    employees[scanuserid] = {
                        'name': emp_name,
                        'pm_count': 0,  # KERANI
                        'p1_count': 0,  # MANDOR
                        'p5_count': 0   # ASISTEN
                    }
                
                if recordtag == 'PM':
                    employees[scanuserid]['pm_count'] = count
                    total_kerani += count
                elif recordtag == 'P1':
                    employees[scanuserid]['p1_count'] = count
                    total_mandor += count
                elif recordtag == 'P5':
                    employees[scanuserid]['p5_count'] = count
                    total_asisten += count
            
            total_verifications = total_mandor + total_asisten
            verification_rate = (total_verifications / total_kerani * 100) if total_kerani > 0 else 0
            
            return {
                'div_id': div_id,
                'div_name': div_name,
                'employees': employees,
                'totals': {
                    'kerani': total_kerani,
                    'mandor': total_mandor,
                    'asisten': total_asisten,
                    'verifications': total_verifications,
                    'verification_rate': verification_rate
                }
            }
            
        except Exception as e:
            self.log_message(f"Error analyzing {div_name}: {str(e)}")
            return None
    
    def generate_reports(self):
        """Generate Excel and PDF reports"""
        try:
            self.progress_var.set("Membuat laporan...")
            
            # Create output directory
            output_dir = "reports"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generate Excel report
            if self.generate_excel_var.get():
                excel_path = self.create_excel_report(output_dir, timestamp)
                self.log_message(f"Laporan Excel: {excel_path}")
            
            # Generate PDF report
            if self.generate_pdf_var.get():
                pdf_path = self.create_pdf_report(output_dir, timestamp)
                self.log_message(f"Laporan PDF: {pdf_path}")
            
            self.log_message("Laporan berhasil dibuat!")
            
        except Exception as e:
            self.log_message(f"Error membuat laporan: {str(e)}")
    
    def create_excel_report(self, output_dir, timestamp):
        """Create Excel report"""
        filename = f"ffb_analysis_report_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for result in self.analysis_results:
                totals = result['totals']
                summary_data.append({
                    'Division': result['div_name'],
                    'Total_KERANI_PM': totals['kerani'],
                    'Total_MANDOR_P1': totals['mandor'],
                    'Total_ASISTEN_P5': totals['asisten'],
                    'Total_Verifications': totals['verifications'],
                    'Verification_Rate': f"{totals['verification_rate']:.2f}%"
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detail sheets per division
            for result in self.analysis_results:
                div_name = result['div_name']
                employees = result['employees']
                totals = result['totals']
                
                detail_data = []
                
                # Add employee data
                for emp_id, emp_data in employees.items():
                    # KERANI row
                    if emp_data['pm_count'] > 0:
                        contribution = (emp_data['pm_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                        detail_data.append({
                            'Division': div_name,
                            'Scanner_User': emp_data['name'],
                            'Scanner_User_ID': emp_id,
                            'Role': 'KERANI',
                            'Conductor': 0,
                            'Assistant': 0,
                            'Manager': 0,
                            'Bunch_Counter': emp_data['pm_count'],
                            'Contribution_Pct': f"{contribution:.2f}%"
                        })
                    
                    # MANDOR row
                    if emp_data['p1_count'] > 0:
                        contribution = (emp_data['p1_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                        detail_data.append({
                            'Division': div_name,
                            'Scanner_User': emp_data['name'],
                            'Scanner_User_ID': emp_id,
                            'Role': 'MANDOR',
                            'Conductor': emp_data['p1_count'],
                            'Assistant': 0,
                            'Manager': 0,
                            'Bunch_Counter': 0,
                            'Contribution_Pct': f"{contribution:.2f}%"
                        })
                    
                    # ASISTEN row
                    if emp_data['p5_count'] > 0:
                        contribution = (emp_data['p5_count'] / totals['kerani'] * 100) if totals['kerani'] > 0 else 0
                        detail_data.append({
                            'Division': div_name,
                            'Scanner_User': emp_data['name'],
                            'Scanner_User_ID': emp_id,
                            'Role': 'ASISTEN',
                            'Conductor': 0,
                            'Assistant': emp_data['p5_count'],
                            'Manager': 0,
                            'Bunch_Counter': 0,
                            'Contribution_Pct': f"{contribution:.2f}%"
                        })
                
                # Add summary rows
                detail_data.append({
                    'Division': '',
                    'Scanner_User': f'Total KERANI: {totals["kerani"]}',
                    'Scanner_User_ID': f'Total Verifications: {totals["verifications"]}',
                    'Role': f'Verification Rate: {totals["verification_rate"]:.2f}%',
                    'Conductor': '',
                    'Assistant': '',
                    'Manager': '',
                    'Bunch_Counter': '',
                    'Contribution_Pct': ''
                })
                
                detail_df = pd.DataFrame(detail_data)
                sheet_name = div_name.replace('/', '_').replace('\\', '_')[:31]
                detail_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return filepath
    
    def create_pdf_report(self, output_dir, timestamp):
        """Create PDF report"""
        filename = f"ffb_analysis_report_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create comprehensive PDF report
        try:
            # Generate PDF using the FFB PDF generator
            pdf_path = generate_ffb_pdf_report(
                self.analysis_results,  # Pass the analysis results directly
                output_dir,
                filename
            )
            
            return pdf_path if pdf_path else filepath
            
        except Exception as e:
            self.log_message(f"PDF generation error: {str(e)}")
            return filepath
    
    def log_message(self, message):
        """Log message to results text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_results(self):
        """Clear results text area"""
        self.results_text.delete(1.0, tk.END)
    
    def open_output_folder(self):
        """Open output folder"""
        output_dir = "reports"
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showinfo("Info", "Folder output belum ada")

def main():
    """Main function"""
    root = tk.Tk()
    app = FFBScannerAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 