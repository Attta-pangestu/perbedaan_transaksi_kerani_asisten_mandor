"""
Export Options Widget
Widget for selecting export format and output location
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path
import os


class ExportOptionsWidget(ttk.Frame):
    """
    Widget for selecting export options
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize export options widget
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        # Export settings
        self.selected_formats: List[str] = []
        self.output_directory = ""
        self.filename_prefix = ""
        self.include_timestamp = True
        self.open_after_export = True
        
        # Available formats
        self.available_formats = {
            'PDF': {
                'extension': '.pdf',
                'description': 'Portable Document Format',
                'icon': '📄'
            },
            'Excel': {
                'extension': '.xlsx',
                'description': 'Microsoft Excel Workbook',
                'icon': '📊'
            },
            'CSV': {
                'extension': '.csv',
                'description': 'Comma Separated Values',
                'icon': '📋'
            },
            'JSON': {
                'extension': '.json',
                'description': 'JavaScript Object Notation',
                'icon': '📝'
            }
        }
        
        # Callbacks
        self.on_change: Optional[Callable] = None
        
        # Setup UI
        self.setup_ui()
        
        # Set default values
        self.set_default_values()
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Format selection frame
        format_frame = ttk.LabelFrame(self, text="Format Export", padding="10")
        format_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        format_frame.columnconfigure(0, weight=1)
        
        # Format checkboxes
        self.format_vars = {}
        self.format_checkboxes = {}
        
        for i, (format_name, format_info) in enumerate(self.available_formats.items()):
            var = tk.BooleanVar()
            self.format_vars[format_name] = var
            
            checkbox = ttk.Checkbutton(
                format_frame,
                text=f"{format_info['icon']} {format_name} ({format_info['description']})",
                variable=var,
                command=self._on_format_changed
            )
            checkbox.grid(row=i, column=0, sticky=tk.W, pady=2)
            self.format_checkboxes[format_name] = checkbox
        
        # Output location frame
        location_frame = ttk.LabelFrame(self, text="Lokasi Output", padding="10")
        location_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        location_frame.columnconfigure(1, weight=1)
        
        # Output directory
        ttk.Label(location_frame, text="Direktori:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        dir_frame = ttk.Frame(location_frame)
        dir_frame.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(10, 0), pady=2)
        dir_frame.columnconfigure(0, weight=1)
        
        self.directory_var = tk.StringVar()
        self.directory_entry = ttk.Entry(dir_frame, textvariable=self.directory_var, font=('Arial', 9))
        self.directory_entry.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 5))
        self.directory_entry.bind('<KeyRelease>', self._on_directory_changed)
        
        self.browse_button = ttk.Button(
            dir_frame,
            text="Browse...",
            command=self.browse_directory
        )
        self.browse_button.grid(row=0, column=1)
        
        # Filename prefix
        ttk.Label(location_frame, text="Prefix File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.prefix_var = tk.StringVar()
        self.prefix_entry = ttk.Entry(
            location_frame,
            textvariable=self.prefix_var,
            font=('Arial', 9)
        )
        self.prefix_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(10, 0), pady=2)
        self.prefix_entry.bind('<KeyRelease>', self._on_prefix_changed)
        
        # Options frame
        options_frame = ttk.LabelFrame(self, text="Opsi Tambahan", padding="10")
        options_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Include timestamp
        self.timestamp_var = tk.BooleanVar()
        self.timestamp_checkbox = ttk.Checkbutton(
            options_frame,
            text="Sertakan timestamp dalam nama file",
            variable=self.timestamp_var,
            command=self._on_timestamp_changed
        )
        self.timestamp_checkbox.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Open after export
        self.open_after_var = tk.BooleanVar()
        self.open_after_checkbox = ttk.Checkbutton(
            options_frame,
            text="Buka file setelah export",
            variable=self.open_after_var,
            command=self._on_open_after_changed
        )
        self.open_after_checkbox.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self, text="Preview Nama File", padding="10")
        preview_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        
        # Preview text
        self.preview_text = tk.Text(
            preview_frame,
            height=4,
            wrap=tk.WORD,
            font=('Arial', 9),
            state=tk.DISABLED,
            bg='#f8f8f8'
        )
        self.preview_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Status frame
        status_frame = ttk.Frame(self)
        status_frame.grid(row=4, column=0, sticky=tk.W+tk.E)
        
        # Validation status
        self.status_label = ttk.Label(status_frame, text="", font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT)
        
        # Export info
        self.info_label = ttk.Label(status_frame, text="", font=('Arial', 8))
        self.info_label.pack(side=tk.RIGHT)
    
    def set_default_values(self):
        """Set default values"""
        # Default formats
        self.format_vars['PDF'].set(True)
        
        # Default directory (current working directory)
        default_dir = os.path.join(os.getcwd(), "reports")
        self.directory_var.set(default_dir)
        
        # Default prefix
        self.prefix_var.set("laporan")
        
        # Default options
        self.timestamp_var.set(True)
        self.open_after_var.set(True)
        
        # Update internal state
        self._update_internal_state()
        self._update_preview()
        self._validate_settings()
    
    def _on_format_changed(self):
        """Handle format selection change"""
        self._update_internal_state()
        self._update_preview()
        self._validate_settings()
        self._notify_change()
    
    def _on_directory_changed(self, event=None):
        """Handle directory change"""
        self.output_directory = self.directory_var.get()
        self._update_preview()
        self._validate_settings()
        self._notify_change()
    
    def _on_prefix_changed(self, event=None):
        """Handle prefix change"""
        self.filename_prefix = self.prefix_var.get()
        self._update_preview()
        self._notify_change()
    
    def _on_timestamp_changed(self):
        """Handle timestamp option change"""
        self.include_timestamp = self.timestamp_var.get()
        self._update_preview()
        self._notify_change()
    
    def _on_open_after_changed(self):
        """Handle open after export option change"""
        self.open_after_export = self.open_after_var.get()
        self._notify_change()
    
    def _update_internal_state(self):
        """Update internal state from UI"""
        self.selected_formats = [
            format_name for format_name, var in self.format_vars.items()
            if var.get()
        ]
    
    def _update_preview(self):
        """Update filename preview"""
        if not self.selected_formats:
            preview_text = "Pilih format untuk melihat preview nama file"
        else:
            preview_lines = []
            
            # Generate sample filenames
            base_name = self.filename_prefix or "laporan"
            
            if self.include_timestamp:
                timestamp = "2024-01-15_14-30-00"  # Sample timestamp
                base_name += f"_{timestamp}"
            
            for format_name in self.selected_formats:
                extension = self.available_formats[format_name]['extension']
                filename = f"{base_name}{extension}"
                
                if self.output_directory:
                    full_path = os.path.join(self.output_directory, filename)
                    preview_lines.append(full_path)
                else:
                    preview_lines.append(filename)
            
            preview_text = "\n".join(preview_lines)
        
        # Update preview text widget
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state=tk.DISABLED)
    
    def _validate_settings(self):
        """Validate export settings"""
        errors = []
        warnings = []
        
        # Check if at least one format is selected
        if not self.selected_formats:
            errors.append("Pilih minimal satu format export")
        
        # Check output directory
        if self.output_directory:
            if not os.path.exists(os.path.dirname(self.output_directory)):
                warnings.append("Direktori parent tidak ada")
        else:
            warnings.append("Direktori output tidak ditentukan")
        
        # Check filename prefix
        if not self.filename_prefix:
            warnings.append("Prefix file kosong")
        elif any(char in self.filename_prefix for char in '<>:"/\\|?*'):
            errors.append("Prefix file mengandung karakter tidak valid")
        
        # Update status
        if errors:
            self.status_label.config(text=f"✗ {'; '.join(errors)}", foreground='red')
        elif warnings:
            self.status_label.config(text=f"⚠ {'; '.join(warnings)}", foreground='orange')
        else:
            self.status_label.config(text="✓ Pengaturan valid", foreground='green')
        
        # Update info
        format_count = len(self.selected_formats)
        self.info_label.config(text=f"{format_count} format dipilih")
    
    def browse_directory(self):
        """Browse for output directory"""
        initial_dir = self.directory_var.get() or os.getcwd()
        
        directory = filedialog.askdirectory(
            title="Pilih Direktori Output",
            initialdir=initial_dir
        )
        
        if directory:
            self.directory_var.set(directory)
            self._on_directory_changed()
    
    def get_export_settings(self) -> Dict[str, Any]:
        """
        Get current export settings
        
        Returns:
            Export settings dictionary
        """
        return {
            'formats': self.selected_formats.copy(),
            'output_directory': self.output_directory,
            'filename_prefix': self.filename_prefix,
            'include_timestamp': self.include_timestamp,
            'open_after_export': self.open_after_export
        }
    
    def set_export_settings(self, settings: Dict[str, Any]):
        """
        Set export settings
        
        Args:
            settings: Export settings dictionary
        """
        # Set formats
        for format_name, var in self.format_vars.items():
            var.set(format_name in settings.get('formats', []))
        
        # Set directory
        if 'output_directory' in settings:
            self.directory_var.set(settings['output_directory'])
        
        # Set prefix
        if 'filename_prefix' in settings:
            self.prefix_var.set(settings['filename_prefix'])
        
        # Set options
        if 'include_timestamp' in settings:
            self.timestamp_var.set(settings['include_timestamp'])
        
        if 'open_after_export' in settings:
            self.open_after_var.set(settings['open_after_export'])
        
        # Update internal state
        self._update_internal_state()
        self._update_preview()
        self._validate_settings()
    
    def validate_settings(self) -> bool:
        """
        Validate current settings
        
        Returns:
            True if settings are valid
        """
        # Must have at least one format
        if not self.selected_formats:
            return False
        
        # Must have valid directory
        if self.output_directory:
            try:
                # Check if we can create the directory
                Path(self.output_directory).mkdir(parents=True, exist_ok=True)
            except Exception:
                return False
        
        # Must have valid filename prefix
        if not self.filename_prefix:
            return False
        
        if any(char in self.filename_prefix for char in '<>:"/\\|?*'):
            return False
        
        return True
    
    def get_output_filenames(self, base_name: str = None) -> Dict[str, str]:
        """
        Get output filenames for each format
        
        Args:
            base_name: Base filename (uses prefix if not provided)
            
        Returns:
            Dictionary mapping format to full file path
        """
        if base_name is None:
            base_name = self.filename_prefix or "laporan"
        
        # Add timestamp if enabled
        if self.include_timestamp:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_name += f"_{timestamp}"
        
        filenames = {}
        for format_name in self.selected_formats:
            extension = self.available_formats[format_name]['extension']
            filename = f"{base_name}{extension}"
            
            if self.output_directory:
                full_path = os.path.join(self.output_directory, filename)
            else:
                full_path = filename
            
            filenames[format_name] = full_path
        
        return filenames
    
    def create_output_directory(self) -> bool:
        """
        Create output directory if it doesn't exist
        
        Returns:
            True if directory exists or was created successfully
        """
        if not self.output_directory:
            return False
        
        try:
            Path(self.output_directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuat direktori: {str(e)}")
            return False
    
    def get_available_formats(self) -> List[str]:
        """
        Get list of available formats
        
        Returns:
            List of format names
        """
        return list(self.available_formats.keys())
    
    def set_available_formats(self, formats: List[str]):
        """
        Set available formats (updates UI)
        
        Args:
            formats: List of format names to make available
        """
        # Hide all checkboxes first
        for checkbox in self.format_checkboxes.values():
            checkbox.grid_remove()
        
        # Show only available formats
        row = 0
        for format_name in formats:
            if format_name in self.format_checkboxes:
                self.format_checkboxes[format_name].grid(row=row, column=0, sticky=tk.W, pady=2)
                row += 1
    
    def clear_selection(self):
        """Clear all format selections"""
        for var in self.format_vars.values():
            var.set(False)
        
        self._update_internal_state()
        self._update_preview()
        self._validate_settings()
        self._notify_change()
    
    def select_all_formats(self):
        """Select all available formats"""
        for var in self.format_vars.values():
            var.set(True)
        
        self._update_internal_state()
        self._update_preview()
        self._validate_settings()
        self._notify_change()
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable the widget
        
        Args:
            enabled: Whether to enable the widget
        """
        state = "normal" if enabled else "disabled"
        
        # Format checkboxes
        for checkbox in self.format_checkboxes.values():
            checkbox.config(state=state)
        
        # Entry fields
        self.directory_entry.config(state=state)
        self.prefix_entry.config(state=state)
        
        # Buttons
        self.browse_button.config(state=state)
        
        # Option checkboxes
        self.timestamp_checkbox.config(state=state)
        self.open_after_checkbox.config(state=state)
    
    def _notify_change(self):
        """Notify change callback"""
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass  # Ignore callback errors
    
    def get_export_summary(self) -> str:
        """
        Get export settings summary
        
        Returns:
            Summary text
        """
        if not self.selected_formats:
            return "Tidak ada format yang dipilih"
        
        summary_parts = []
        
        # Formats
        formats_text = ", ".join(self.selected_formats)
        summary_parts.append(f"Format: {formats_text}")
        
        # Directory
        if self.output_directory:
            summary_parts.append(f"Direktori: {self.output_directory}")
        
        # Prefix
        if self.filename_prefix:
            summary_parts.append(f"Prefix: {self.filename_prefix}")
        
        # Options
        options = []
        if self.include_timestamp:
            options.append("timestamp")
        if self.open_after_export:
            options.append("buka otomatis")
        
        if options:
            summary_parts.append(f"Opsi: {', '.join(options)}")
        
        return " | ".join(summary_parts)