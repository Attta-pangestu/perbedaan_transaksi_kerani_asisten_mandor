"""
GUI Application for Ifess Database Analysis
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import calendar
from datetime import datetime
import threading
import subprocess
import re

class IfessAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ifess Database Analysis")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set up the main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the form
        self.create_form()
        
        # Create the output area
        self.create_output_area()
        
        # Create the buttons
        self.create_buttons()
        
        # Initialize variables
        self.process = None
        self.output_thread = None
        self.running = False
        
    def create_form(self):
        # Create a frame for the form
        form_frame = ttk.LabelFrame(self.main_frame, text="Configuration", padding="10")
        form_frame.pack(fill=tk.X, pady=10)
        
        # Database selection
        db_frame = ttk.Frame(form_frame)
        db_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(db_frame, text="Database Path:").pack(side=tk.LEFT, padx=5)
        
        self.db_path_var = tk.StringVar(value="D:\\Gawean Rebinmas\\Monitoring Database\\Database Ifess\\PTRJ_P1A_08042025\\PTRJ_P1A.FDB")
        self.db_path_entry = ttk.Entry(db_frame, textvariable=self.db_path_var, width=50)
        self.db_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(db_frame, text="Browse", command=self.browse_db)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # ISQL Path
        isql_frame = ttk.Frame(form_frame)
        isql_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(isql_frame, text="ISQL Path:").pack(side=tk.LEFT, padx=5)
        
        self.isql_path_var = tk.StringVar(value="C:\\Program Files (x86)\\Firebird\\Firebird_1_5\\bin\\isql.exe")
        self.isql_path_entry = ttk.Entry(isql_frame, textvariable=self.isql_path_var, width=50)
        self.isql_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_isql_button = ttk.Button(isql_frame, text="Browse", command=self.browse_isql)
        self.browse_isql_button.pack(side=tk.LEFT, padx=5)
        
        # Database credentials
        cred_frame = ttk.Frame(form_frame)
        cred_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cred_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.username_var = tk.StringVar(value="sysdba")
        self.username_entry = ttk.Entry(cred_frame, textvariable=self.username_var, width=15)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(cred_frame, text="Password:").pack(side=tk.LEFT, padx=5)
        self.password_var = tk.StringVar(value="masterkey")
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, width=15, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        # Period selection
        period_frame = ttk.Frame(form_frame)
        period_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(period_frame, text="Month:").pack(side=tk.LEFT, padx=5)
        
        # Month dropdown
        self.month_var = tk.IntVar(value=datetime.now().month)
        month_names = list(calendar.month_name)[1:]  # Skip the empty first element
        self.month_combo = ttk.Combobox(period_frame, textvariable=self.month_var, 
                                        values=list(range(1, 13)), width=5)
        self.month_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(period_frame, text="Year:").pack(side=tk.LEFT, padx=5)
        
        # Year entry
        current_year = datetime.now().year
        self.year_var = tk.IntVar(value=current_year)
        years = list(range(current_year - 5, current_year + 6))
        self.year_combo = ttk.Combobox(period_frame, textvariable=self.year_var, 
                                       values=years, width=6)
        self.year_combo.pack(side=tk.LEFT, padx=5)
        
        # Output directory
        output_frame = ttk.Frame(form_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
        
        self.output_dir_var = tk.StringVar(value="reports")
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_output_button = ttk.Button(output_frame, text="Browse", command=self.browse_output)
        self.browse_output_button.pack(side=tk.LEFT, padx=5)
        
        # Output format
        format_frame = ttk.Frame(form_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=5)
        
        self.excel_var = tk.BooleanVar(value=True)
        self.excel_check = ttk.Checkbutton(format_frame, text="Excel", variable=self.excel_var)
        self.excel_check.pack(side=tk.LEFT, padx=5)
        
        self.pdf_var = tk.BooleanVar(value=True)
        self.pdf_check = ttk.Checkbutton(format_frame, text="PDF", variable=self.pdf_var)
        self.pdf_check.pack(side=tk.LEFT, padx=5)
        
        # Data limit
        limit_frame = ttk.Frame(form_frame)
        limit_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(limit_frame, text="Data Limit (optional):").pack(side=tk.LEFT, padx=5)
        
        self.limit_var = tk.StringVar(value="")
        self.limit_entry = ttk.Entry(limit_frame, textvariable=self.limit_var, width=10)
        self.limit_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(limit_frame, text="(Leave empty for no limit)").pack(side=tk.LEFT, padx=5)
        
    def create_output_area(self):
        # Create a frame for the output
        output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a text widget for the output
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=15, width=80)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
    def create_buttons(self):
        # Create a frame for the buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create the buttons
        self.run_button = ttk.Button(button_frame, text="Run Analysis", command=self.run_analysis)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Output", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.open_output_button = ttk.Button(button_frame, text="Open Output Directory", command=self.open_output_dir)
        self.open_output_button.pack(side=tk.RIGHT, padx=5)
        
    def browse_db(self):
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("Firebird Database", "*.FDB"), ("All Files", "*.*")]
        )
        if file_path:
            self.db_path_var.set(file_path)
            
    def browse_isql(self):
        file_path = filedialog.askopenfilename(
            title="Select ISQL Executable",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            self.isql_path_var.set(file_path)
            
    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir_var.set(dir_path)
            
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        
    def open_output_dir(self):
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.startfile(output_dir)
        
    def run_analysis(self):
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Disable the run button and enable the stop button
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True
        
        # Clear the output
        self.clear_output()
        
        # Get the database name from the path
        db_path = self.db_path_var.get()
        db_name = os.path.splitext(os.path.basename(db_path))[0]
        
        # Get the month name
        month = self.month_var.get()
        month_name = calendar.month_name[month]
        
        # Build the command
        cmd = [
            sys.executable,  # Python executable
            "analisis_perbedaan_panen.py",
            "--db-path", self.db_path_var.get(),
            "--isql-path", self.isql_path_var.get(),
            "--username", self.username_var.get(),
            "--password", self.password_var.get(),
            "--month", str(self.month_var.get()),
            "--year", str(self.year_var.get()),
            "--output-dir", self.output_dir_var.get()
        ]
        
        # Add optional arguments
        if self.excel_var.get():
            cmd.append("--excel")
        if self.pdf_var.get():
            cmd.append("--pdf")
        
        limit = self.limit_var.get().strip()
        if limit and limit.isdigit():
            cmd.extend(["--limit", limit])
            
        # Run the command in a separate thread
        self.output_text.insert(tk.END, f"Running analysis for {month_name} {self.year_var.get()}...\n")
        self.output_text.insert(tk.END, f"Database: {db_path}\n")
        self.output_text.insert(tk.END, f"Database Name: {db_name}\n\n")
        self.output_text.see(tk.END)
        
        # Start the process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Start a thread to read the output
        self.output_thread = threading.Thread(target=self.read_output)
        self.output_thread.daemon = True
        self.output_thread.start()
        
    def read_output(self):
        """Read the output from the process and update the GUI."""
        for line in iter(self.process.stdout.readline, ''):
            if not self.running:
                break
            self.output_text.insert(tk.END, line)
            self.output_text.see(tk.END)
            
        # Process has finished
        self.process.stdout.close()
        return_code = self.process.wait()
        
        # Update the GUI
        self.root.after(0, self.process_finished, return_code)
        
    def process_finished(self, return_code):
        """Called when the process has finished."""
        self.running = False
        self.process = None
        
        # Enable the run button and disable the stop button
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Show a message
        if return_code == 0:
            self.output_text.insert(tk.END, "\nAnalysis completed successfully.\n")
        else:
            self.output_text.insert(tk.END, f"\nAnalysis failed with return code {return_code}.\n")
        self.output_text.see(tk.END)
        
    def stop_analysis(self):
        """Stop the analysis process."""
        if self.process:
            self.running = False
            self.process.terminate()
            self.output_text.insert(tk.END, "\nAnalysis stopped by user.\n")
            self.output_text.see(tk.END)
            
            # Enable the run button and disable the stop button
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def validate_inputs(self):
        """Validate the user inputs."""
        # Check if the database file exists
        if not os.path.exists(self.db_path_var.get()):
            messagebox.showerror("Error", "Database file does not exist.")
            return False
        
        # Check if the ISQL executable exists
        if not os.path.exists(self.isql_path_var.get()):
            messagebox.showerror("Error", "ISQL executable does not exist.")
            return False
        
        # Check if the month is valid
        month = self.month_var.get()
        if month < 1 or month > 12:
            messagebox.showerror("Error", "Month must be between 1 and 12.")
            return False
        
        # Check if the year is valid
        year = self.year_var.get()
        if year < 1900 or year > 2100:
            messagebox.showerror("Error", "Year must be between 1900 and 2100.")
            return False
        
        # Check if at least one output format is selected
        if not self.excel_var.get() and not self.pdf_var.get():
            messagebox.showerror("Error", "At least one output format must be selected.")
            return False
        
        # Check if the limit is a valid number
        limit = self.limit_var.get().strip()
        if limit and not limit.isdigit():
            messagebox.showerror("Error", "Limit must be a number.")
            return False
        
        return True

def extract_database_name(db_path):
    """Extract the database name from the path."""
    # Extract the filename without extension
    filename = os.path.basename(db_path)
    name, _ = os.path.splitext(filename)
    return name

def main():
    root = tk.Tk()
    app = IfessAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
