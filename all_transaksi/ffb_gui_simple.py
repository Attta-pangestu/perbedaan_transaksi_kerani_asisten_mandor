#!/usr/bin/env python3
"""
GUI Sederhana untuk FFB Scanner Analysis dengan Date Range Picker
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import os

# Try to import tkcalendar, if not available use simple date entry
try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

from firebird_connector import FirebirdConnector
from correct_analysis_engine import analyze_multiple_divisions, get_divisions_list, get_employee_names
from pdf_report_generator import FFBReportGenerator

# Alias for compatibility
def get_divisions(connector):
    return get_divisions_list(connector)

class SimpleFFBGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FFB Scanner Analysis - Date Range Selector")
        self.root.geometry("600x500")
        
        # Database configuration
        self.db_path = "C:\\Users\\nbgmf\\Downloads\\PTRJ_P1A\\PTRJ_P1A.FDB"
        self.connector = None
        self.employee_mapping = {}
        self.divisions = []
        
        self.setup_ui()
        self.connect_database()
    
    def setup_ui(self):
        """Setup user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="FFB Scanner Verification Analysis", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Date range frame
        date_frame = ttk.LabelFrame(main_frame, text="Pilih Rentang Tanggal", padding="10")
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date inputs
        date_input_frame = ttk.Frame(date_frame)
        date_input_frame.pack(fill=tk.X)
        
        # Start date
        ttk.Label(date_input_frame, text="Tanggal Mulai:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        if HAS_CALENDAR:
            self.start_date = DateEntry(date_input_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            self.start_date_var = tk.StringVar(value="2025-04-01")
            self.start_date = ttk.Entry(date_input_frame, textvariable=self.start_date_var, width=15)
        
        self.start_date.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # End date
        ttk.Label(date_input_frame, text="Tanggal Akhir:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        if HAS_CALENDAR:
            self.end_date = DateEntry(date_input_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            self.end_date_var = tk.StringVar(value="2025-04-29")
            self.end_date = ttk.Entry(date_input_frame, textvariable=self.end_date_var, width=15)
        
        self.end_date.grid(row=0, column=3, sticky=tk.W)
        
        # Set default dates
        if HAS_CALENDAR:
            self.start_date.set_date(datetime(2025, 4, 1))
            self.end_date.set_date(datetime(2025, 4, 28))
        
        # Quick date buttons
        quick_frame = ttk.Frame(date_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(quick_frame, text="April 2025 (Test)", command=self.set_april_2025).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_frame, text="Bulan Ini", command=self.set_this_month).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_frame, text="Bulan Lalu", command=self.set_last_month).pack(side=tk.LEFT)
        
        # Division selection
        div_frame = ttk.LabelFrame(main_frame, text="Pilih Divisi", padding="10")
        div_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Division mode
        self.division_mode = tk.StringVar(value="specific")
        mode_frame = ttk.Frame(div_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Semua Divisi", variable=self.division_mode, 
                       value="all").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="Divisi Tertentu", variable=self.division_mode, 
                       value="specific").pack(side=tk.LEFT)
        
        # Division listbox
        list_frame = ttk.Frame(div_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.division_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.division_listbox.yview)
        self.division_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.division_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.analyze_button = ttk.Button(button_frame, text="Mulai Analisis", 
                                        command=self.start_analysis)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = ttk.Label(button_frame, text="Siap")
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
    
    def connect_database(self):
        """Connect to database and load divisions"""
        try:
            self.connector = FirebirdConnector(self.db_path)
            if self.connector.test_connection():
                self.status_label.config(text="Database terhubung")
                self.load_divisions()
                self.load_employee_mapping()
            else:
                self.status_label.config(text="Koneksi database gagal")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def load_divisions(self):
        """Load divisions into listbox"""
        try:
            self.divisions = get_divisions(self.connector)
            self.division_listbox.delete(0, tk.END)
            
            # Add target divisions first
            target_divisions = [
                ('15', 'Air Batu'),
                ('16', 'Air Kundo'), 
                ('17', 'Air Hijau')
            ]
            
            for div_id, div_name in target_divisions:
                self.division_listbox.insert(tk.END, f"{div_name} (ID: {div_id})")
            
            # Add separator
            self.division_listbox.insert(tk.END, "--- Divisi Lainnya ---")
            
            # Add other divisions
            for division in self.divisions:
                div_name = division.get('div_name', 'Unknown')
                div_id = division.get('div_id', 'Unknown')
                if div_id not in ['15', '16', '17']:
                    self.division_listbox.insert(tk.END, f"{div_name} (ID: {div_id})")
            
            # Select target divisions by default
            for i in range(3):
                self.division_listbox.selection_set(i)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading divisions: {str(e)}")
    
    def load_employee_mapping(self):
        """Load employee mapping"""
        try:
            self.employee_mapping = get_employee_names(self.connector)
        except Exception as e:
            print(f"Error loading employee mapping: {e}")
    
    def get_date_values(self):
        """Get date values from inputs"""
        if HAS_CALENDAR:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
        else:
            try:
                start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
                end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Format tanggal harus YYYY-MM-DD")
        
        return start_date, end_date
    
    def set_april_2025(self):
        """Set to April 2025 test period"""
        if HAS_CALENDAR:
            self.start_date.set_date(datetime(2025, 4, 1))
            self.end_date.set_date(datetime(2025, 4, 29))
        else:
            self.start_date_var.set("2025-04-01")
            self.end_date_var.set("2025-04-29")
    
    def set_this_month(self):
        """Set to current month"""
        today = datetime.now()
        first_day = today.replace(day=1)
        
        if HAS_CALENDAR:
            self.start_date.set_date(first_day)
            self.end_date.set_date(today)
        else:
            self.start_date_var.set(first_day.strftime('%Y-%m-%d'))
            self.end_date_var.set(today.strftime('%Y-%m-%d'))
    
    def set_last_month(self):
        """Set to last month"""
        today = datetime.now()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        if HAS_CALENDAR:
            self.start_date.set_date(first_day_last_month)
            self.end_date.set_date(last_day_last_month)
        else:
            self.start_date_var.set(first_day_last_month.strftime('%Y-%m-%d'))
            self.end_date_var.set(last_day_last_month.strftime('%Y-%m-%d'))
    
    def get_selected_divisions(self):
        """Get selected divisions"""
        if self.division_mode.get() == "all":
            return self.divisions
        else:
            selected_indices = self.division_listbox.curselection()
            selected_divisions = []
            
            for i in selected_indices:
                item_text = self.division_listbox.get(i)
                if "---" not in item_text:  # Skip separator
                    # Extract division ID from text like "Air Batu (ID: 15)"
                    if "(ID: " in item_text:
                        div_id = item_text.split("(ID: ")[1].rstrip(")")
                        div_name = item_text.split(" (ID: ")[0]
                        selected_divisions.append({'div_id': div_id, 'div_name': div_name})
            
            return selected_divisions
    
    def start_analysis(self):
        """Start analysis in background thread"""
        try:
            # Validate inputs
            start_date, end_date = self.get_date_values()
            
            if start_date >= end_date:
                messagebox.showerror("Error", "Tanggal mulai harus sebelum tanggal akhir")
                return
            
            selected_divisions = self.get_selected_divisions()
            if not selected_divisions:
                messagebox.showerror("Error", "Pilih minimal satu divisi")
                return
            
            # Start analysis
            self.analyze_button.config(state=tk.DISABLED)
            self.progress.start()
            self.status_label.config(text="Analisis berjalan...")
            
            # Run in background thread
            thread = threading.Thread(target=self.run_analysis, 
                                     args=(selected_divisions, start_date, end_date))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run_analysis(self, selected_divisions, start_date, end_date):
        """Run analysis in background"""
        try:
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Memulai analisis..."))

            # Use correct analysis engine
            division_results = analyze_multiple_divisions(
                self.connector, selected_divisions, start_date, end_date)

            if division_results:
                # Generate reports
                self.root.after(0, lambda: self.status_label.config(text="Membuat laporan Excel dan PDF..."))

                output_dir = "reports"
                os.makedirs(output_dir, exist_ok=True)

                # Generate Excel report
                excel_path = self.generate_excel_report(division_results, output_dir)

                # Generate PDF reports
                pdf_generator = FFBReportGenerator()
                pdf_reports = pdf_generator.generate_complete_report(division_results, output_dir)

                # Show success message
                self.root.after(0, lambda: self.show_success_with_reports(excel_path, pdf_reports, division_results))
            else:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "Tidak ada data ditemukan"))
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error dalam analisis: {error_msg}"))
        finally:
            # Reset UI
            self.root.after(0, self.analysis_finished)
    
    def generate_excel_report(self, division_results, output_dir):
        """Generate Excel report"""
        import pandas as pd
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FFB_Analysis_Report_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for result in division_results:
                stats = result['verification_stats']
                summary_data.append({
                    'Division': result['div_name'],
                    'Total_KERANI': stats['total_kerani_transactions'],
                    'Total_MANDOR': stats['total_mandor_transactions'],
                    'Total_ASISTEN': stats['total_asisten_transactions'],
                    'Verification_Rate': f"{stats['verification_rate']:.2f}%"
                })

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Detail sheets per division
            for result in division_results:
                div_name = result['div_name']
                employees = result['employees']

                detail_data = []
                for emp_id, emp_data in employees.items():
                    if emp_data['PM'] > 0:  # KERANI
                        detail_data.append({
                            'Division': div_name,
                            'Scanner_User': emp_data['name'],
                            'Scanner_User_ID': emp_id,
                            'Role': 'KERANI',
                            'Conductor': 0,
                            'Assistant': 0,
                            'Manager': 0,
                            'Bunch_Counter': emp_data['PM']
                        })
                    if emp_data['P1'] > 0:  # MANDOR
                        detail_data.append({
                            'Division': div_name,
                            'Scanner_User': emp_data['name'],
                            'Scanner_User_ID': emp_id,
                            'Role': 'MANDOR',
                            'Conductor': emp_data['P1'],
                            'Assistant': 0,
                            'Manager': 0,
                            'Bunch_Counter': 0
                        })
                    if emp_data['P5'] > 0:  # ASISTEN
                        detail_data.append({
                            'Division': div_name,
                            'Scanner_User': emp_data['name'],
                            'Scanner_User_ID': emp_id,
                            'Role': 'ASISTEN',
                            'Conductor': 0,
                            'Assistant': emp_data['P5'],
                            'Manager': 0,
                            'Bunch_Counter': 0
                        })

                if detail_data:
                    detail_df = pd.DataFrame(detail_data)
                    sheet_name = div_name.replace(' ', '_')[:31]
                    detail_df.to_excel(writer, sheet_name=sheet_name, index=False)

        return filepath

    def show_success_with_reports(self, excel_path, pdf_reports, division_results):
        """Show success message with multiple reports"""
        message = "✅ Analisis selesai!\n\n"
        message += f"📊 Excel Report: {os.path.basename(excel_path)}\n"
        message += f"📄 PDF Summary: {os.path.basename(pdf_reports['summary_report'])}\n"
        message += f"📋 PDF Details: {len(pdf_reports['division_reports'])} files\n\n"

        # Add verification for Air Kundo
        for result in division_results:
            if result['div_name'] == 'Air Kundo' and '4771' in result['employees']:
                erly_pm = result['employees']['4771']['PM']
                message += f"🎯 Erly (4771): {erly_pm} transaksi PM\n"
                message += f"Expected: 123 - {'✅ MATCH' if erly_pm == 123 else '❌ MISMATCH'}\n\n"

        # Add summary
        for result in division_results:
            div_name = result['div_name']
            stats = result['verification_stats']
            message += f"{div_name}: {stats['verification_rate']:.2f}% verification rate\n"

        if messagebox.askyesno("Sukses", message + "\nBuka folder laporan?"):
            os.startfile("reports")
    
    def analysis_finished(self):
        """Reset UI after analysis"""
        self.analyze_button.config(state=tk.NORMAL)
        self.progress.stop()
        self.status_label.config(text="Siap")

def main():
    """Main function"""
    root = tk.Tk()
    
    # Check if tkcalendar is available
    if not HAS_CALENDAR:
        messagebox.showinfo("Info", "tkcalendar tidak tersedia. Menggunakan input teks untuk tanggal.\nFormat: YYYY-MM-DD")
    
    app = SimpleFFBGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
