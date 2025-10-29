"""
Main Modular FFB Analysis Application

This is the main entry point for the modular FFB analysis system.
It provides a GUI interface that can dynamically load and use different templates
for FFB analysis and reporting.

Author: Generated for Modular FFB Analysis System
Date: 2024
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import threading
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add core modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import core modules
from core.database_connector import DatabaseConnectorFactory, DatabaseConfig
from core.template_loader import TemplateManager
from core.template_base import BaseTemplate


class ModularFFBAnalysisGUI:
    """
    Main GUI application for modular FFB analysis system
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modular FFB Analysis System - PT. REBINMAS JAYA")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Initialize components
        self.database_connector = None
        self.template_manager = None
        self.current_template = None
        self.analysis_thread = None
        self.is_analysis_running = False
        
        # GUI variables
        self.db_path_var = tk.StringVar(value=r"D:\Gawean Rebinmas\Monitoring Database\Database Ifess\IFESS_2B_24-10-2025\PTRJ_P2B.FDB")
        self.db_user_var = tk.StringVar(value="SYSDBA")
        self.db_password_var = tk.StringVar(value="masterkey")
        self.selected_template_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Siap")
        self.progress_var = tk.DoubleVar()
        
        # Initialize GUI
        self.setup_gui()
        self.setup_template_manager()
        
        # Load saved configuration
        self.load_saved_config()
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Database configuration tab
        self.setup_database_tab()
        
        # Template selection tab
        self.setup_template_tab()
        
        # Analysis tab
        self.setup_analysis_tab()
        
        # Results tab
        self.setup_results_tab()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_database_tab(self):
        """Setup database configuration tab"""
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="Konfigurasi Database")
        
        # Database configuration section
        db_config_frame = ttk.LabelFrame(db_frame, text="Pengaturan Database Firebird", padding="10")
        db_config_frame.pack(fill="x", padx=10, pady=10)
        
        # Database path
        ttk.Label(db_config_frame, text="Path Database:").grid(row=0, column=0, sticky="w", pady=5)
        db_path_frame = ttk.Frame(db_config_frame)
        db_path_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        db_config_frame.columnconfigure(1, weight=1)
        
        ttk.Entry(db_path_frame, textvariable=self.db_path_var, width=50).pack(side="left", fill="x", expand=True)
        ttk.Button(db_path_frame, text="Browse", command=self.browse_database).pack(side="right", padx=(5, 0))
        
        # Database credentials
        ttk.Label(db_config_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(db_config_frame, textvariable=self.db_user_var, width=20).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        ttk.Label(db_config_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(db_config_frame, textvariable=self.db_password_var, show="*", width=20).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Database actions
        db_action_frame = ttk.Frame(db_config_frame)
        db_action_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(db_action_frame, text="Test Koneksi", command=self.test_database_connection).pack(side="left", padx=(0, 5))
        ttk.Button(db_action_frame, text="Load Database", command=self.load_database).pack(side="left", padx=5)
        ttk.Button(db_action_frame, text="Simpan Konfigurasi", command=self.save_config).pack(side="left", padx=5)
        
        # Connection status
        self.connection_status_label = ttk.Label(db_config_frame, text="Status: Belum terhubung", foreground="red")
        self.connection_status_label.grid(row=4, column=0, columnspan=2, pady=10)
    
    def setup_template_tab(self):
        """Setup template selection tab"""
        template_frame = ttk.Frame(self.notebook)
        self.notebook.add(template_frame, text="Pilih Template")
        
        # Template selection section
        template_select_frame = ttk.LabelFrame(template_frame, text="Pilih Template Analisis", padding="10")
        template_select_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(template_select_frame, text="Template yang Tersedia:").pack(anchor="w", pady=(0, 5))
        
        # Template listbox
        template_list_frame = ttk.Frame(template_select_frame)
        template_list_frame.pack(fill="both", expand=True)
        
        self.template_listbox = tk.Listbox(template_list_frame, height=8)
        self.template_listbox.pack(side="left", fill="both", expand=True)
        self.template_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        template_scrollbar = ttk.Scrollbar(template_list_frame, orient="vertical", command=self.template_listbox.yview)
        template_scrollbar.pack(side="right", fill="y")
        self.template_listbox.configure(yscrollcommand=template_scrollbar.set)
        
        # Template actions
        template_action_frame = ttk.Frame(template_select_frame)
        template_action_frame.pack(fill="x", pady=10)
        
        ttk.Button(template_action_frame, text="Refresh Templates", command=self.refresh_templates).pack(side="left", padx=(0, 5))
        ttk.Button(template_action_frame, text="Load Template", command=self.load_selected_template).pack(side="left", padx=5)
        
        # Template info
        self.template_info_frame = ttk.LabelFrame(template_frame, text="Informasi Template", padding="10")
        self.template_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.template_info_text = tk.Text(self.template_info_frame, height=10, wrap="word", state="disabled")
        self.template_info_text.pack(fill="both", expand=True)
        
        info_scrollbar = ttk.Scrollbar(self.template_info_frame, orient="vertical", command=self.template_info_text.yview)
        info_scrollbar.pack(side="right", fill="y")
        self.template_info_text.configure(yscrollcommand=info_scrollbar.set)
    
    def setup_analysis_tab(self):
        """Setup analysis configuration tab"""
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Analisis")
        
        # Template-specific configuration will be added here dynamically
        self.template_config_frame = ttk.Frame(self.analysis_frame)
        self.template_config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Analysis controls
        analysis_control_frame = ttk.Frame(self.analysis_frame)
        analysis_control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(analysis_control_frame, text="Mulai Analisis", command=self.start_analysis).pack(side="left", padx=(0, 5))
        ttk.Button(analysis_control_frame, text="Stop Analisis", command=self.stop_analysis).pack(side="left", padx=5)
        ttk.Button(analysis_control_frame, text="Reset", command=self.reset_analysis).pack(side="left", padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(self.analysis_frame)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side="left")
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(10, 0))
    
    def setup_results_tab(self):
        """Setup results display tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Hasil")
        
        # Results display
        results_display_frame = ttk.LabelFrame(results_frame, text="Log Analisis", padding="10")
        results_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text = tk.Text(results_display_frame, wrap="word", state="disabled")
        self.results_text.pack(side="left", fill="both", expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_display_frame, orient="vertical", command=self.results_text.yview)
        results_scrollbar.pack(side="right", fill="y")
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        # Results actions
        results_action_frame = ttk.Frame(results_frame)
        results_action_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(results_action_frame, text="Clear Log", command=self.clear_results).pack(side="left", padx=(0, 5))
        ttk.Button(results_action_frame, text="Save Log", command=self.save_log).pack(side="left", padx=5)
        ttk.Button(results_action_frame, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=5)
    
    def setup_status_bar(self):
        """Setup status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom")
        
        ttk.Label(status_frame, text="Status:").pack(side="left", padx=(10, 5))
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left")
        
        # Current template indicator
        ttk.Label(status_frame, text="Template:").pack(side="right", padx=(5, 5))
        self.current_template_label = ttk.Label(status_frame, text="Tidak ada", foreground="gray")
        self.current_template_label.pack(side="right", padx=(0, 10))
    
    def setup_template_manager(self):
        """Initialize template manager"""
        try:
            templates_dir = os.path.join(current_dir, "templates")
            self.template_manager = TemplateManager(templates_dir)
            self.refresh_templates()
        except Exception as e:
            self.log_message(f"Error initializing template manager: {str(e)}")
    
    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            title="Pilih Database Firebird",
            filetypes=[("Firebird Database", "*.fdb"), ("All files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)
    
    def test_database_connection(self):
        """Test database connection"""
        try:
            if not self.db_path_var.get():
                messagebox.showerror("Error", "Pilih file database terlebih dahulu")
                return
            
            # Create connector with correct parameters
            connector = DatabaseConnectorFactory.create_connector(
                'firebird',
                db_path=self.db_path_var.get(),
                username=self.db_user_var.get(),
                password=self.db_password_var.get()
            )
            
            # Test connection
            if connector.test_connection():
                self.connection_status_label.config(text="Status: Terhubung", foreground="green")
                messagebox.showinfo("Sukses", "Koneksi database berhasil!")
                return True
            else:
                self.connection_status_label.config(text="Status: Gagal terhubung", foreground="red")
                messagebox.showerror("Error", "Koneksi database gagal!")
                return False
                
        except Exception as e:
            self.connection_status_label.config(text="Status: Error", foreground="red")
            messagebox.showerror("Error", f"Error testing connection: {str(e)}")
            return False
    
    def load_database(self):
        """Load database and initialize connector"""
        try:
            if not self.test_database_connection():
                return
            
            # Create connector with correct parameters
            self.database_connector = DatabaseConnectorFactory.create_connector(
                'firebird',
                db_path=self.db_path_var.get(),
                username=self.db_user_var.get(),
                password=self.db_password_var.get()
            )
            
            self.log_message("Database loaded successfully")
            self.status_var.set("Database terhubung")
            
            # Load divisions if template is selected
            if self.current_template:
                self.load_template_divisions()
                
        except Exception as e:
            self.log_message(f"Error loading database: {str(e)}")
            messagebox.showerror("Error", f"Error loading database: {str(e)}")
    
    def refresh_templates(self):
        """Refresh available templates list"""
        try:
            if self.template_manager:
                self.template_manager.reload_templates()
                templates = self.template_manager.get_available_templates()
                
                self.template_listbox.delete(0, tk.END)
                for template_name in templates:
                    self.template_listbox.insert(tk.END, template_name)
                
                self.log_message(f"Found {len(templates)} templates")
        except Exception as e:
            self.log_message(f"Error refreshing templates: {str(e)}")
    
    def on_template_select(self, event):
        """Handle template selection"""
        try:
            selection = self.template_listbox.curselection()
            if selection:
                template_name = self.template_listbox.get(selection[0])
                self.show_template_info(template_name)
        except Exception as e:
            self.log_message(f"Error selecting template: {str(e)}")
    
    def show_template_info(self, template_name: str):
        """Show template information"""
        try:
            template_info = self.template_manager.get_template_info(template_name)
            
            self.template_info_text.config(state="normal")
            self.template_info_text.delete(1.0, tk.END)
            
            if template_info:
                info_text = f"Nama: {template_info.get('name', 'N/A')}\n"
                info_text += f"Versi: {template_info.get('version', 'N/A')}\n"
                info_text += f"Deskripsi: {template_info.get('description', 'N/A')}\n"
                info_text += f"Author: {template_info.get('author', 'N/A')}\n"
                info_text += f"Template Class: {template_info.get('template_class', 'N/A')}\n\n"
                
                # Add configuration details
                if 'gui_config' in template_info:
                    info_text += "Konfigurasi GUI:\n"
                    gui_config = template_info['gui_config']
                    for key, value in gui_config.items():
                        info_text += f"  {key}: {value}\n"
                    info_text += "\n"
                
                if 'business_logic_config' in template_info:
                    info_text += "Konfigurasi Business Logic:\n"
                    bl_config = template_info['business_logic_config']
                    for key, value in bl_config.items():
                        if isinstance(value, dict):
                            info_text += f"  {key}:\n"
                            for sub_key, sub_value in value.items():
                                info_text += f"    {sub_key}: {sub_value}\n"
                        else:
                            info_text += f"  {key}: {value}\n"
                    info_text += "\n"
                
                self.template_info_text.insert(1.0, info_text)
            else:
                self.template_info_text.insert(1.0, "Template information not available")
            
            self.template_info_text.config(state="disabled")
            
        except Exception as e:
            self.log_message(f"Error showing template info: {str(e)}")
    
    def load_selected_template(self):
        """Load the selected template"""
        try:
            selection = self.template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Pilih template terlebih dahulu")
                return
            
            template_name = self.template_listbox.get(selection[0])
            
            # Load template
            template = self.template_manager.get_template(template_name)
            if not template:
                messagebox.showerror("Error", f"Gagal memuat template: {template_name}")
                return
            
            # Initialize template
            if not template.initialize_template():
                messagebox.showerror("Error", f"Gagal menginisialisasi template: {template_name}")
                return
            
            self.current_template = template
            self.current_template_label.config(text=template_name, foreground="blue")
            
            # Setup template GUI
            self.setup_template_gui()
            
            # Load divisions if database is connected
            if self.database_connector:
                self.load_template_divisions()
            
            self.log_message(f"Template '{template_name}' loaded successfully")
            self.status_var.set(f"Template '{template_name}' dimuat")
            
            # Switch to analysis tab
            self.notebook.select(2)  # Analysis tab
            
        except Exception as e:
            self.log_message(f"Error loading template: {str(e)}")
            messagebox.showerror("Error", f"Error loading template: {str(e)}")
    
    def setup_template_gui(self):
        """Setup template-specific GUI"""
        try:
            # Clear existing template GUI
            for widget in self.template_config_frame.winfo_children():
                widget.destroy()
            
            if self.current_template:
                gui_handler = self.current_template.get_gui_handler()
                if gui_handler:
                    gui_handler.create_template_frame(self.template_config_frame)
                    self.log_message("Template GUI setup completed")
        except Exception as e:
            self.log_message(f"Error setting up template GUI: {str(e)}")
    
    def load_template_divisions(self):
        """Load divisions for current template"""
        try:
            if self.current_template and self.database_connector:
                divisions = self.current_template.load_divisions(self.database_connector)
                gui_handler = self.current_template.get_gui_handler()
                if gui_handler and hasattr(gui_handler, 'populate_divisions'):
                    gui_handler.populate_divisions(divisions)
                    self.log_message(f"Loaded {len(divisions)} divisions")
        except Exception as e:
            self.log_message(f"Error loading divisions: {str(e)}")
    
    def start_analysis(self):
        """Start analysis process"""
        try:
            if not self.current_template:
                messagebox.showwarning("Warning", "Pilih template terlebih dahulu")
                return
            
            if not self.database_connector:
                messagebox.showwarning("Warning", "Koneksi database diperlukan")
                return
            
            if self.is_analysis_running:
                messagebox.showwarning("Warning", "Analisis sedang berjalan")
                return
            
            # Validate template inputs
            gui_handler = self.current_template.get_gui_handler()
            if gui_handler:
                is_valid, message = gui_handler.validate_inputs()
                if not is_valid:
                    messagebox.showerror("Validation Error", message)
                    return
            
            # Start analysis in separate thread
            self.is_analysis_running = True
            self.analysis_thread = threading.Thread(target=self.run_analysis)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            self.status_var.set("Analisis berjalan...")
            self.log_message("Analysis started")
            
        except Exception as e:
            self.is_analysis_running = False
            self.log_message(f"Error starting analysis: {str(e)}")
            messagebox.showerror("Error", f"Error starting analysis: {str(e)}")
    
    def run_analysis(self):
        """Run analysis in separate thread"""
        try:
            self.progress_var.set(0)
            
            # Get template inputs
            gui_handler = self.current_template.get_gui_handler()
            template_inputs = gui_handler.get_template_inputs() if gui_handler else {}
            
            self.progress_var.set(10)
            self.log_message("Getting template inputs...")
            
            # Execute analysis
            analysis_params = {
                'output_directory': os.path.join(current_dir, 'output'),
                'generate_excel': True,
                'generate_pdf': True
            }
            
            self.progress_var.set(20)
            self.log_message("Starting template analysis...")
            
            # Run template analysis
            success = self.current_template.execute_analysis(
                self.database_connector,
                template_inputs,
                analysis_params
            )
            
            self.progress_var.set(100)
            
            if success:
                self.log_message("Analysis completed successfully!")
                self.status_var.set("Analisis selesai")
                self.root.after(0, lambda: messagebox.showinfo("Success", "Analisis berhasil diselesaikan!"))
            else:
                self.log_message("Analysis failed!")
                self.status_var.set("Analisis gagal")
                self.root.after(0, lambda: messagebox.showerror("Error", "Analisis gagal!"))
            
        except Exception as e:
            self.log_message(f"Analysis error: {str(e)}")
            self.status_var.set("Error analisis")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis error: {str(e)}"))
        finally:
            self.is_analysis_running = False
            self.progress_var.set(0)
    
    def stop_analysis(self):
        """Stop running analysis"""
        if self.is_analysis_running:
            self.is_analysis_running = False
            self.log_message("Analysis stopped by user")
            self.status_var.set("Analisis dihentikan")
    
    def reset_analysis(self):
        """Reset analysis inputs"""
        try:
            if self.current_template:
                gui_handler = self.current_template.get_gui_handler()
                if gui_handler and hasattr(gui_handler, 'reset_inputs'):
                    gui_handler.reset_inputs()
                    self.log_message("Analysis inputs reset")
        except Exception as e:
            self.log_message(f"Error resetting analysis: {str(e)}")
    
    def log_message(self, message: str):
        """Log message to results text"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            self.results_text.config(state="normal")
            self.results_text.insert(tk.END, log_entry)
            self.results_text.see(tk.END)
            self.results_text.config(state="disabled")
        except Exception as e:
            print(f"Error logging message: {str(e)}")
    
    def clear_results(self):
        """Clear results log"""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")
    
    def save_log(self):
        """Save log to file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Log",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Log saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving log: {str(e)}")
    
    def open_output_folder(self):
        """Open output folder"""
        try:
            output_dir = os.path.join(current_dir, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            os.startfile(output_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Error opening output folder: {str(e)}")
    
    def save_config(self):
        """Save current configuration"""
        try:
            config = {
                'database_path': self.db_path_var.get(),
                'database_user': self.db_user_var.get(),
                'database_password': self.db_password_var.get(),
                'last_template': self.current_template.template_name if self.current_template else None
            }
            
            config_path = os.path.join(current_dir, 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration: {str(e)}")
    
    def load_saved_config(self):
        """Load saved configuration"""
        try:
            config_path = os.path.join(current_dir, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.db_path_var.set(config.get('database_path', ''))
                self.db_user_var.set(config.get('database_user', 'SYSDBA'))
                self.db_password_var.set(config.get('database_password', 'masterkey'))
                
                self.log_message("Configuration loaded")
        except Exception as e:
            self.log_message(f"Error loading configuration: {str(e)}")
    
    def run(self):
        """Run the application"""
        try:
            self.log_message("Modular FFB Analysis System started")
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Application error: {str(e)}")


def main():
    """Main entry point"""
    try:
        app = ModularFFBAnalysisGUI()
        app.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        messagebox.showerror("Fatal Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()