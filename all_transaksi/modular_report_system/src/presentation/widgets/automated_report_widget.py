"""
Automated Report Management Widget
Provides interface for managing automated report configurations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Callable, Optional
import logging
from datetime import datetime


class AutomatedReportWidget:
    """Widget for managing automated report configurations"""
    
    def __init__(self, parent, automated_service=None):
        self.parent = parent
        self.automated_service = automated_service
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.on_config_changed = None
        self.on_test_requested = None
        self.on_generate_now_requested = None
        
        # UI Components
        self.main_frame = None
        self.config_tree = None
        self.detail_frame = None
        self.status_label = None
        self.control_buttons = {}
        
        self.setup_ui()
        self.load_configurations()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="🤖 Sistem Laporan Otomatis",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # Create main sections
        self.create_configuration_list()
        self.create_detail_section()
        self.create_control_section()
        self.create_status_section()
    
    def create_configuration_list(self):
        """Create configuration list section"""
        # Configuration list frame
        list_frame = ttk.LabelFrame(self.main_frame, text="📋 Konfigurasi Laporan Otomatis", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for configurations
        columns = ('name', 'unit_estate', 'frequency', 'time', 'last_run', 'status')
        self.config_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.config_tree.heading('name', text='Nama Konfigurasi')
        self.config_tree.heading('unit_estate', text='Unit & Estate')
        self.config_tree.heading('frequency', text='Frekuensi')
        self.config_tree.heading('time', text='Waktu')
        self.config_tree.heading('last_run', text='Terakhir Dijalankan')
        self.config_tree.heading('status', text='Status')
        
        self.config_tree.column('name', width=250)
        self.config_tree.column('unit_estate', width=150)
        self.config_tree.column('frequency', width=120)
        self.config_tree.column('time', width=80)
        self.config_tree.column('last_run', width=150)
        self.config_tree.column('status', width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.config_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.config_tree.bind('<<TreeviewSelect>>', self.on_config_selected)
    
    def create_detail_section(self):
        """Create configuration detail section"""
        self.detail_frame = ttk.LabelFrame(self.main_frame, text="📝 Detail Konfigurasi", padding=10)
        self.detail_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create detail fields
        self.detail_fields = {}
        
        # Row 1: Name and Schedule
        row1 = ttk.Frame(self.detail_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text="Nama:").pack(side=tk.LEFT)
        self.detail_fields['name'] = ttk.Label(row1, text="-", font=('Segoe UI', 9, 'bold'))
        self.detail_fields['name'].pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row1, text="Jadwal:").pack(side=tk.LEFT)
        self.detail_fields['schedule'] = ttk.Label(row1, text="-")
        self.detail_fields['schedule'].pack(side=tk.LEFT, padx=(10, 0))
        
        # Row 2: Estates and Template
        row2 = ttk.Frame(self.detail_frame)
        row2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row2, text="Estate:").pack(side=tk.LEFT)
        self.detail_fields['estates'] = ttk.Label(row2, text="-")
        self.detail_fields['estates'].pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row2, text="Template:").pack(side=tk.LEFT)
        self.detail_fields['template'] = ttk.Label(row2, text="-")
        self.detail_fields['template'].pack(side=tk.LEFT, padx=(10, 0))
        
        # Row 3: Export Format and Options
        row3 = ttk.Frame(self.detail_frame)
        row3.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row3, text="Format:").pack(side=tk.LEFT)
        self.detail_fields['format'] = ttk.Label(row3, text="-")
        self.detail_fields['format'].pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row3, text="Opsi:").pack(side=tk.LEFT)
        self.detail_fields['options'] = ttk.Label(row3, text="-")
        self.detail_fields['options'].pack(side=tk.LEFT, padx=(10, 0))
        
        # Row 4: Description
        row4 = ttk.Frame(self.detail_frame)
        row4.pack(fill=tk.X)
        
        ttk.Label(row4, text="Deskripsi:").pack(side=tk.LEFT)
        self.detail_fields['description'] = ttk.Label(row4, text="-", wraplength=400)
        self.detail_fields['description'].pack(side=tk.LEFT, padx=(10, 0))
    
    def create_control_section(self):
        """Create control buttons section"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side buttons
        left_buttons = ttk.Frame(control_frame)
        left_buttons.pack(side=tk.LEFT)
        
        self.control_buttons['enable'] = ttk.Button(
            left_buttons,
            text="✅ Aktifkan",
            command=self.toggle_configuration,
            state=tk.DISABLED
        )
        self.control_buttons['enable'].pack(side=tk.LEFT, padx=(0, 5))
        
        self.control_buttons['test'] = ttk.Button(
            left_buttons,
            text="🧪 Test Konfigurasi",
            command=self.test_configuration,
            state=tk.DISABLED
        )
        self.control_buttons['test'].pack(side=tk.LEFT, padx=(0, 5))
        
        self.control_buttons['generate_now'] = ttk.Button(
            left_buttons,
            text="🚀 Generate Sekarang",
            command=self.generate_now,
            state=tk.DISABLED
        )
        self.control_buttons['generate_now'].pack(side=tk.LEFT, padx=(0, 5))
        
        # Add default config button
        self.control_buttons['add_default'] = ttk.Button(
            left_buttons,
            text="⚙️ Tambah Default Unit 9 Estate 2B",
            command=self.add_default_configurations
        )
        self.control_buttons['add_default'].pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttk.Frame(control_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        self.control_buttons['refresh'] = ttk.Button(
            right_buttons,
            text="🔄 Refresh",
            command=self.refresh_configurations
        )
        self.control_buttons['refresh'].pack(side=tk.LEFT, padx=(5, 0))
    
    def create_status_section(self):
        """Create status display section"""
        status_frame = ttk.LabelFrame(self.main_frame, text="📊 Status Sistem", padding=10)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame,
            text="🟢 Sistem siap untuk generate report",
            font=('Segoe UI', 9)
        )
        self.status_label.pack()
        
        # Last activity log
        self.activity_text = tk.Text(status_frame, height=4, wrap=tk.WORD)
        self.activity_text.pack(fill=tk.X, pady=(10, 0))
        
        # Scrollbar for activity log
        activity_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=activity_scroll.set)
    
    def load_configurations(self):
        """Load and display automated report configurations"""
        try:
            # Clear existing items
            for item in self.config_tree.get_children():
                self.config_tree.delete(item)
            
            # Load configurations from service
            configs = self.automated_service.get_automated_configs()
            
            for config in configs:
                # Format unit and estate display
                unit_estate = f"Unit {config.get('unit', 'N/A')} - Estate {config.get('estate', 'N/A')}"
                
                # Format frequency and time
                frequency = config.get('frequency', 'Manual')
                time_str = config.get('time', 'N/A')
                
                # Format last run
                last_run = config.get('last_run', 'Belum pernah')
                if last_run and last_run != 'Belum pernah':
                    try:
                        from datetime import datetime
                        if isinstance(last_run, str):
                            last_run_dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                            last_run = last_run_dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                
                # Determine status
                status = "Aktif" if config.get('enabled', False) else "Nonaktif"
                
                self.config_tree.insert("", "end", values=(
                    config.get('name', 'Tanpa Nama'),
                    unit_estate,
                    frequency,
                    time_str,
                    last_run,
                    status
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat konfigurasi: {str(e)}")
            print(f"Error loading configurations: {e}")
    
    def add_default_configurations(self):
        """Add default configurations for Unit 9 and Estate 2B"""
        try:
            # Configuration for Unit 9 - Estate 2B
            default_config = {
                'name': 'Laporan Harian Unit 9 Estate 2B',
                'unit': '9',
                'estate': '2B',
                'frequency': 'Harian',
                'time': '08:00',
                'enabled': True,
                'report_type': 'comprehensive',
                'output_format': 'excel',
                'email_recipients': [],
                'created_at': datetime.now().isoformat()
            }
            
            # Save configuration
            config_id = self.automated_service.save_configuration(default_config)
            
            if config_id:
                messagebox.showinfo("Sukses", "Konfigurasi default untuk Unit 9 Estate 2B berhasil ditambahkan!")
                self.load_configurations()
            else:
                messagebox.showerror("Error", "Gagal menambahkan konfigurasi default")
                
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan konfigurasi default: {str(e)}")
            print(f"Error adding default configuration: {e}")
    
    def on_config_selected(self, event):
        """Handle configuration selection"""
        try:
            selection = self.config_tree.selection()
            if not selection:
                self.clear_detail_fields()
                self.disable_control_buttons()
                return
            
            # Get selected configuration
            item = self.config_tree.item(selection[0])
            config_name = item['values'][0]
            
            # Find configuration by name
            configs = self.automated_service.get_automated_configs()
            selected_config = None
            selected_key = None
            
            for key, config in configs.items():
                if config.get('name') == config_name:
                    selected_config = config
                    selected_key = key
                    break
            
            if selected_config:
                self.update_detail_fields(selected_config)
                self.enable_control_buttons(selected_key, selected_config)
            
        except Exception as e:
            self.logger.error(f"Error handling selection: {e}")
    
    def update_detail_fields(self, config: Dict):
        """Update detail fields with configuration data"""
        try:
            self.detail_fields['name'].config(text=config.get('name', '-'))
            self.detail_fields['schedule'].config(text=config.get('schedule', '-').title())
            
            estates = ', '.join([estate['name'] for estate in config.get('estates', [])])
            self.detail_fields['estates'].config(text=estates or '-')
            
            template = config.get('template', {}).get('name', '-')
            self.detail_fields['template'].config(text=template)
            
            self.detail_fields['format'].config(text=config.get('export_format', '-').upper())
            
            options = []
            if config.get('include_charts', False):
                options.append('Charts')
            if config.get('include_summary', False):
                options.append('Summary')
            if config.get('auto_email', False):
                options.append('Auto Email')
            
            self.detail_fields['options'].config(text=', '.join(options) or '-')
            self.detail_fields['description'].config(text=config.get('description', '-'))
            
        except Exception as e:
            self.logger.error(f"Error updating detail fields: {e}")
    
    def clear_detail_fields(self):
        """Clear all detail fields"""
        for field in self.detail_fields.values():
            field.config(text='-')
    
    def enable_control_buttons(self, config_key: str, config: Dict):
        """Enable control buttons for selected configuration"""
        self.selected_config_key = config_key
        self.selected_config = config
        
        # Enable/disable buttons based on configuration state
        enabled = config.get('enabled', False)
        
        self.control_buttons['enable'].config(
            state=tk.NORMAL,
            text="❌ Nonaktifkan" if enabled else "✅ Aktifkan"
        )
        self.control_buttons['test'].config(state=tk.NORMAL)
        self.control_buttons['generate_now'].config(
            state=tk.NORMAL if enabled else tk.DISABLED
        )
    
    def disable_control_buttons(self):
        """Disable all control buttons"""
        self.selected_config_key = None
        self.selected_config = None
        
        for button_name in ['enable', 'test', 'generate_now']:
            self.control_buttons[button_name].config(state=tk.DISABLED)
    
    def toggle_configuration(self):
        """Toggle configuration enabled/disabled state"""
        try:
            if not self.selected_config_key:
                return
            
            current_state = self.selected_config.get('enabled', False)
            new_state = not current_state
            
            success = self.automated_service.enable_config(self.selected_config_key, new_state)
            
            if success:
                action = "diaktifkan" if new_state else "dinonaktifkan"
                messagebox.showinfo("Sukses", f"Konfigurasi berhasil {action}")
                self.refresh_configurations()
                self.log_activity(f"Konfigurasi {self.selected_config['name']} {action}")
            else:
                messagebox.showerror("Error", "Gagal mengubah status konfigurasi")
                
        except Exception as e:
            self.logger.error(f"Error toggling configuration: {e}")
            messagebox.showerror("Error", f"Error: {e}")
    
    def test_configuration(self):
        """Test selected configuration"""
        try:
            if not self.selected_config_key:
                return
            
            self.log_activity(f"Testing konfigurasi {self.selected_config['name']}...")
            
            result = self.automated_service.test_configuration(self.selected_config_key)
            
            if result['success']:
                details = result.get('request_details', {})
                message = f"""Test berhasil!

Detail Request:
• Bulan: {details.get('month', '-')} / {details.get('year', '-')}
• Estate: {', '.join(details.get('estates', []))}
• Template: {details.get('template', '-')}
• Format: {details.get('export_format', '-')}

{result.get('message', '')}"""
                
                messagebox.showinfo("Test Berhasil", message)
                self.log_activity(f"Test konfigurasi {self.selected_config['name']} berhasil")
            else:
                messagebox.showerror("Test Gagal", f"Test gagal: {result['error']}")
                self.log_activity(f"Test konfigurasi {self.selected_config['name']} gagal: {result['error']}")
                
        except Exception as e:
            self.logger.error(f"Error testing configuration: {e}")
            messagebox.showerror("Error", f"Error testing: {e}")
    
    def generate_now(self):
        """Generate report now for selected configuration"""
        try:
            if not self.selected_config_key:
                return
            
            # Confirm action
            if not messagebox.askyesno(
                "Konfirmasi", 
                f"Generate laporan sekarang untuk '{self.selected_config['name']}'?"
            ):
                return
            
            self.log_activity(f"Memulai generasi laporan {self.selected_config['name']}...")
            
            # Start generation in background
            success = self.automated_service.generate_report_now(self.selected_config_key)
            
            if success:
                messagebox.showinfo("Sukses", "Generasi laporan dimulai. Periksa status untuk progress.")
            else:
                messagebox.showerror("Error", "Gagal memulai generasi laporan")
                
        except Exception as e:
            self.logger.error(f"Error generating report now: {e}")
            messagebox.showerror("Error", f"Error: {e}")
    
    def refresh_configurations(self):
        """Refresh configuration list"""
        self.load_configurations()
        self.clear_detail_fields()
        self.disable_control_buttons()
        self.log_activity("Konfigurasi di-refresh")
    
    def log_activity(self, message: str):
        """Log activity to the activity text widget"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            self.activity_text.insert(tk.END, log_message)
            self.activity_text.see(tk.END)
            
            # Keep only last 50 lines
            lines = self.activity_text.get("1.0", tk.END).split('\n')
            if len(lines) > 50:
                self.activity_text.delete("1.0", f"{len(lines)-50}.0")
            
        except Exception as e:
            self.logger.error(f"Error logging activity: {e}")
    
    def set_automated_service(self, service):
        """Set the automated report service"""
        self.automated_service = service
        
        # Add status callback
        if service:
            service.add_status_callback(self.on_status_update)
        
        self.load_configurations()
    
    def on_status_update(self, config_name: str, status: str):
        """Handle status updates from automated service"""
        try:
            self.log_activity(f"{config_name}: {status}")
        except Exception as e:
            self.logger.error(f"Error handling status update: {e}")