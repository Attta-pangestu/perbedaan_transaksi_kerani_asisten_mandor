"""
Estate Multi-Select Widget
Widget for selecting multiple estates with checkboxes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional, Callable, Any
import json
from pathlib import Path


class EstateMultiSelectWidget(ttk.Frame):
    """
    Widget for selecting multiple estates with checkboxes
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize estate multi-select widget
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        # Callback for change events
        self.on_change: Optional[Callable] = None
        
        # Estate data
        self.estates: Dict[str, Dict[str, Any]] = {}
        self.estate_vars: Dict[str, tk.BooleanVar] = {}
        
        # UI components
        self.tree: Optional[ttk.Treeview] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 5))
        header_frame.columnconfigure(1, weight=1)
        
        # Select all checkbox
        self.select_all_var = tk.BooleanVar()
        self.select_all_check = ttk.Checkbutton(
            header_frame,
            text="Pilih Semua",
            variable=self.select_all_var,
            command=self._on_select_all
        )
        self.select_all_check.grid(row=0, column=0, sticky=tk.W)
        
        # Estate count label
        self.count_label = ttk.Label(header_frame, text="0 estate tersedia")
        self.count_label.grid(row=0, column=1, sticky=tk.E)
        
        # Main frame for treeview and scrollbar
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create treeview with checkboxes
        self.tree = ttk.Treeview(
            main_frame,
            columns=('status', 'description'),
            show='tree headings',
            height=8
        )
        
        # Configure columns
        self.tree.heading('#0', text='Estate', anchor=tk.W)
        self.tree.heading('status', text='Status', anchor=tk.CENTER)
        self.tree.heading('description', text='Deskripsi', anchor=tk.W)
        
        self.tree.column('#0', width=150, minwidth=100)
        self.tree.column('status', width=80, minwidth=60, anchor=tk.CENTER)
        self.tree.column('description', width=200, minwidth=150)
        
        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        # Bind events
        self.tree.bind('<Button-1>', self._on_tree_click)
        self.tree.bind('<space>', self._on_tree_space)
        
        # Action buttons frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(5, 0))
        
        # Refresh button
        self.refresh_button = ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_estates
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear selection button
        self.clear_button = ttk.Button(
            button_frame,
            text="Hapus Pilihan",
            command=self.clear_selection
        )
        self.clear_button.pack(side=tk.LEFT)
        
        # Start Generate Report button (main action)
        self.start_generate_button = ttk.Button(
            button_frame,
            text="🚀 Start Generate Report",
            command=self.start_generate_report,
            style='Accent.TButton'
        )
        self.start_generate_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Selected count label
        self.selected_label = ttk.Label(button_frame, text="0 dipilih")
        self.selected_label.pack(side=tk.RIGHT)
    
    def load_estates(self):
        """Load estates from configuration"""
        try:
            # Clear existing data
            self.estates.clear()
            self.estate_vars.clear()
            
            # Clear treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load from config file
            config_path = self._get_config_path()
            if config_path and config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Check if this is database_paths.json format
                if config_path.name == 'database_paths.json':
                    # Convert database paths to estate format
                    for estate_code, db_path in config_data.items():
                        self.estates[estate_code] = {
                            "name": estate_code,
                            "description": f"Database: {db_path}",
                            "status": "active",
                            "database_path": db_path
                        }
                # Extract estates from regular config
                elif 'estates' in config_data:
                    self.estates = config_data['estates']
                elif 'estate_configs' in config_data:
                    # Handle different config format
                    for estate_code, estate_data in config_data['estate_configs'].items():
                        self.estates[estate_code] = estate_data
            
            # Add default estates if none found
            if not self.estates:
                self._add_default_estates()
            
            # Populate treeview
            self._populate_treeview()
            
            # Update count
            self._update_count_label()
            
        except Exception as e:
            # Add default estates on error
            self._add_default_estates()
            self._populate_treeview()
            self._update_count_label()
    
    def _get_config_path(self) -> Optional[Path]:
        """Get configuration file path"""
        # Try multiple possible config locations
        possible_paths = [
            Path("config/database_paths.json"),
            Path("../config/database_paths.json"),
            Path("../../config/database_paths.json"),
            Path("../../../config/database_paths.json"),
            Path("config.json"),
            Path("../config.json"),
            Path("../../config.json"),
            Path("../../../config.json"),
            Path("d:/Gawean Rebinmas/Monitoring Database/Laporan_Ifess_beda_transno/all_transaksi/config.json")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _add_default_estates(self):
        """Add default estates - now empty since we only use config"""
        self.estates = {}
        
        self.estates = default_estates
    
    def _populate_treeview(self):
        """Populate treeview with estates"""
        for estate_code, estate_data in self.estates.items():
            # Create boolean variable for checkbox
            var = tk.BooleanVar()
            var.trace('w', lambda *args, code=estate_code: self._on_estate_changed(code))
            self.estate_vars[estate_code] = var
            
            # Get estate info
            name = estate_data.get('name', estate_code)
            description = estate_data.get('description', '')
            status = estate_data.get('status', 'unknown')
            
            # Status display
            status_display = "✓" if status == 'active' else "✗"
            
            # Insert into treeview
            item_id = self.tree.insert(
                '',
                'end',
                text=f"☐ {name} ({estate_code})",
                values=(status_display, description),
                tags=(estate_code,)
            )
            
            # Store item mapping using tags instead of invalid column
            # The estate_code is already stored in tags
    
    def _on_tree_click(self, event):
        """Handle tree click event"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # Get estate code
            estate_code = None
            for tag in self.tree.item(item, 'tags'):
                if tag in self.estate_vars:
                    estate_code = tag
                    break
            
            if estate_code:
                # Toggle checkbox
                current_value = self.estate_vars[estate_code].get()
                self.estate_vars[estate_code].set(not current_value)
    
    def _on_tree_space(self, event):
        """Handle space key press"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Get estate code
            estate_code = None
            for tag in self.tree.item(item, 'tags'):
                if tag in self.estate_vars:
                    estate_code = tag
                    break
            
            if estate_code:
                # Toggle checkbox
                current_value = self.estate_vars[estate_code].get()
                self.estate_vars[estate_code].set(not current_value)
    
    def _on_estate_changed(self, estate_code: str):
        """Handle estate selection change"""
        # Update tree display
        self._update_tree_display()
        
        # Update select all checkbox
        self._update_select_all_state()
        
        # Update selected count
        self._update_selected_count()
        
        # Notify change
        self._notify_change()
    
    def _update_tree_display(self):
        """Update tree display with checkbox states"""
        for item in self.tree.get_children():
            # Get estate code from tags
            estate_code = None
            for tag in self.tree.item(item, 'tags'):
                if tag in self.estate_vars:
                    estate_code = tag
                    break
            
            if estate_code:
                # Update checkbox display
                is_selected = self.estate_vars[estate_code].get()
                current_text = self.tree.item(item, 'text')
                
                # Extract name part (remove checkbox symbol)
                if current_text.startswith('☐ ') or current_text.startswith('☑ '):
                    name_part = current_text[2:]
                else:
                    name_part = current_text
                
                # Update with new checkbox state
                checkbox = '☑' if is_selected else '☐'
                self.tree.item(item, text=f"{checkbox} {name_part}")
    
    def _on_select_all(self):
        """Handle select all checkbox"""
        select_all = self.select_all_var.get()
        
        # Update all estate checkboxes
        for var in self.estate_vars.values():
            var.set(select_all)
    
    def _update_select_all_state(self):
        """Update select all checkbox state"""
        if not self.estate_vars:
            self.select_all_var.set(False)
            return
        
        selected_count = sum(1 for var in self.estate_vars.values() if var.get())
        total_count = len(self.estate_vars)
        
        if selected_count == 0:
            self.select_all_var.set(False)
        elif selected_count == total_count:
            self.select_all_var.set(True)
        # For partial selection, we could use indeterminate state if supported
    
    def _update_count_label(self):
        """Update estate count label"""
        count = len(self.estates)
        self.count_label.config(text=f"{count} estate tersedia")
    
    def _update_selected_count(self):
        """Update selected count label"""
        selected_count = sum(1 for var in self.estate_vars.values() if var.get())
        self.selected_label.config(text=f"{selected_count} dipilih")
    
    def get_selected_estates(self) -> List[str]:
        """
        Get list of selected estate codes
        
        Returns:
            List of selected estate codes
        """
        selected = []
        for estate_code, var in self.estate_vars.items():
            if var.get():
                selected.append(estate_code)
        return selected
    
    def get_selected_estate_info(self) -> List[Dict[str, Any]]:
        """
        Get detailed info for selected estates
        
        Returns:
            List of estate information dictionaries
        """
        selected_info = []
        for estate_code, var in self.estate_vars.items():
            if var.get() and estate_code in self.estates:
                estate_data = self.estates[estate_code].copy()
                estate_data['code'] = estate_code
                selected_info.append(estate_data)
        return selected_info
    
    def set_selected_estates(self, estate_codes: List[str]):
        """
        Set selected estates
        
        Args:
            estate_codes: List of estate codes to select
        """
        # Clear all selections first
        for var in self.estate_vars.values():
            var.set(False)
        
        # Set specified selections
        for estate_code in estate_codes:
            if estate_code in self.estate_vars:
                self.estate_vars[estate_code].set(True)
    
    def clear_selection(self):
        """Clear all selections"""
        for var in self.estate_vars.values():
            var.set(False)
    
    def get_available_estates(self) -> List[str]:
        """
        Get list of all available estate codes
        
        Returns:
            List of all estate codes
        """
        return list(self.estates.keys())
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable the widget
        
        Args:
            enabled: Whether to enable the widget
        """
        state = "normal" if enabled else "disabled"
        
        # Update tree state
        if self.tree:
            self.tree.config(state=state)
        
        # Update buttons
        self.refresh_button.config(state=state)
        self.clear_button.config(state=state)
        self.select_all_check.config(state=state)
        
        # Update tree interaction
        if enabled:
            self.tree.bind('<Button-1>', self._on_tree_click)
            self.tree.bind('<space>', self._on_tree_space)
        else:
            self.tree.unbind('<Button-1>')
            self.tree.unbind('<space>')
    
    def _notify_change(self):
        """Notify change callback"""
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass  # Ignore callback errors
    
    def validate_selection(self) -> bool:
        """
        Validate current selection
        
        Returns:
            True if at least one estate is selected
        """
        return len(self.get_selected_estates()) > 0
    
    def get_selection_summary(self) -> str:
        """
        Get summary of current selection
        
        Returns:
            Summary string
        """
        selected = self.get_selected_estates()
        if not selected:
            return "Tidak ada estate dipilih"
        
        if len(selected) == 1:
            estate_code = selected[0]
            estate_name = self.estates.get(estate_code, {}).get('name', estate_code)
            return f"1 estate dipilih: {estate_name}"
        
        return f"{len(selected)} estate dipilih"
    
    def start_generate_report(self):
        """Start generate report for Unit 9 Estate 2B"""
        try:
            # Confirm action
            if not messagebox.askyesno(
                "Konfirmasi", 
                "Generate laporan untuk Unit 9 Estate 2B sekarang?"
            ):
                return
            
            # Import automated service here to avoid circular imports
            from ...business.services.automated_report_service import AutomatedReportService
            
            # Create service instance
            automated_service = AutomatedReportService()
            
            # Update button state
            self.start_generate_button.config(state=tk.DISABLED, text="⏳ Generating...")
            
            # Start generation process
            success = automated_service.generate_unit9_estate2b_report()
            
            if success:
                self.start_generate_button.config(state=tk.NORMAL, text="🚀 Start Generate Report")
                messagebox.showinfo("Sukses", "Laporan Unit 9 Estate 2B berhasil di-generate!")
            else:
                self.start_generate_button.config(state=tk.NORMAL, text="🚀 Start Generate Report")
                messagebox.showerror("Error", "Gagal generate laporan")
                
        except Exception as e:
            self.start_generate_button.config(state=tk.NORMAL, text="🚀 Start Generate Report")
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")