"""
Template Selection Widget
Widget for selecting report templates
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path

from business.services.template_service import TemplateService
from business.models.report_template import ReportTemplate


class TemplateSelectionWidget(ttk.Frame):
    """
    Widget for selecting report templates
    """
    
    def __init__(self, parent, template_service: TemplateService, **kwargs):
        """
        Initialize template selection widget
        
        Args:
            parent: Parent widget
            template_service: Template service instance
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        self.template_service = template_service
        
        # Callback for change events
        self.on_change: Optional[Callable] = None
        
        # Template data
        self.templates: Dict[str, ReportTemplate] = {}
        self.selected_template: Optional[ReportTemplate] = None
        
        # Setup UI
        self.setup_ui()
        
        # Load templates
        self.refresh_templates()
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 5))
        header_frame.columnconfigure(0, weight=1)
        
        # Template selection combobox
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(
            header_frame,
            textvariable=self.template_var,
            state="readonly",
            font=('Arial', 10)
        )
        self.template_combo.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 10))
        self.template_combo.bind('<<ComboboxSelected>>', self._on_template_selected)
        
        # Refresh button
        self.refresh_button = ttk.Button(
            header_frame,
            text="⟳",
            width=3,
            command=self.refresh_templates
        )
        self.refresh_button.grid(row=0, column=1, sticky=tk.E)
        
        # Template details frame
        details_frame = ttk.LabelFrame(self, text="Detail Template", padding="10")
        details_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(5, 0))
        details_frame.columnconfigure(1, weight=1)
        details_frame.rowconfigure(4, weight=1)
        
        # Template info labels
        ttk.Label(details_frame, text="Nama:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.name_label = ttk.Label(details_frame, text="-", font=('Arial', 9))
        self.name_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(details_frame, text="Versi:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.version_label = ttk.Label(details_frame, text="-", font=('Arial', 9))
        self.version_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(details_frame, text="Format:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.format_label = ttk.Label(details_frame, text="-", font=('Arial', 9))
        self.format_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(details_frame, text="Multi-Estate:", font=('Arial', 9, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.multi_estate_label = ttk.Label(details_frame, text="-", font=('Arial', 9))
        self.multi_estate_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Description
        ttk.Label(details_frame, text="Deskripsi:", font=('Arial', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W+tk.N, pady=(2, 0)
        )
        
        # Description text widget
        desc_frame = ttk.Frame(details_frame)
        desc_frame.grid(row=4, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=(10, 0), pady=(2, 0))
        desc_frame.columnconfigure(0, weight=1)
        desc_frame.rowconfigure(0, weight=1)
        
        self.description_text = tk.Text(
            desc_frame,
            height=4,
            wrap=tk.WORD,
            font=('Arial', 9),
            state=tk.DISABLED,
            bg='#f0f0f0'
        )
        self.description_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Scrollbar for description
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        desc_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        # Status frame
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(5, 0))
        
        # Template count label
        self.count_label = ttk.Label(status_frame, text="0 template tersedia", font=('Arial', 8))
        self.count_label.pack(side=tk.LEFT)
        
        # Validation status
        self.validation_label = ttk.Label(status_frame, text="", font=('Arial', 8))
        self.validation_label.pack(side=tk.RIGHT)
    
    def refresh_templates(self):
        """Refresh available templates"""
        try:
            # Clear current data
            self.templates.clear()
            self.selected_template = None
            
            # Load templates from service
            available_templates = self.template_service.get_available_templates()
            
            # Update templates dictionary
            template_options = []
            for template in available_templates:
                template_key = f"{template.name} (v{template.version})"
                self.templates[template_key] = template
                template_options.append(template_key)
            
            # Update combobox
            self.template_combo['values'] = template_options
            
            # Clear selection
            self.template_var.set("")
            
            # Update UI
            self._update_template_details(None)
            self._update_count_label()
            
            # Notify change
            self._notify_change()
            
        except Exception as e:
            # Handle error
            self.template_combo['values'] = []
            self.template_var.set("")
            self._update_template_details(None)
            self._update_count_label()
            self.validation_label.config(text=f"Error: {str(e)}", foreground='red')
    
    def _on_template_selected(self, event=None):
        """Handle template selection"""
        selected_key = self.template_var.get()
        
        if selected_key and selected_key in self.templates:
            self.selected_template = self.templates[selected_key]
            self._update_template_details(self.selected_template)
            self._validate_template()
        else:
            self.selected_template = None
            self._update_template_details(None)
        
        # Notify change
        self._notify_change()
    
    def _update_template_details(self, template: Optional[ReportTemplate]):
        """Update template details display"""
        if template:
            # Update labels
            self.name_label.config(text=template.name)
            self.version_label.config(text=f"v{template.version}")
            
            # Format supported formats
            formats = template.get_supported_formats()
            format_text = ", ".join(formats) if formats else "Tidak diketahui"
            self.format_label.config(text=format_text)
            
            # Multi-estate support
            multi_estate = "Ya" if template.supports_multi_estate() else "Tidak"
            self.multi_estate_label.config(text=multi_estate)
            
            # Description
            description = template.description or "Tidak ada deskripsi"
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, description)
            self.description_text.config(state=tk.DISABLED)
            
        else:
            # Clear all fields
            self.name_label.config(text="-")
            self.version_label.config(text="-")
            self.format_label.config(text="-")
            self.multi_estate_label.config(text="-")
            
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, "Pilih template untuk melihat detail")
            self.description_text.config(state=tk.DISABLED)
    
    def _validate_template(self):
        """Validate selected template"""
        if not self.selected_template:
            self.validation_label.config(text="", foreground='black')
            return
        
        try:
            # Validate template
            is_valid = self.selected_template.is_valid()
            
            if is_valid:
                self.validation_label.config(text="✓ Template valid", foreground='green')
            else:
                validation_errors = self.selected_template.validate()
                error_text = "; ".join(validation_errors) if validation_errors else "Template tidak valid"
                self.validation_label.config(text=f"✗ {error_text}", foreground='red')
                
        except Exception as e:
            self.validation_label.config(text=f"✗ Error validasi: {str(e)}", foreground='red')
    
    def _update_count_label(self):
        """Update template count label"""
        count = len(self.templates)
        self.count_label.config(text=f"{count} template tersedia")
    
    def get_selected_template(self) -> Optional[ReportTemplate]:
        """
        Get selected template
        
        Returns:
            Selected template or None
        """
        return self.selected_template
    
    def set_selected_template(self, template_name: str, template_version: str = None):
        """
        Set selected template by name and version
        
        Args:
            template_name: Template name
            template_version: Template version (optional)
        """
        # Find matching template
        for key, template in self.templates.items():
            if template.name == template_name:
                if template_version is None or template.version == template_version:
                    self.template_var.set(key)
                    self._on_template_selected()
                    return
    
    def clear_selection(self):
        """Clear template selection"""
        self.template_var.set("")
        self.selected_template = None
        self._update_template_details(None)
        self.validation_label.config(text="", foreground='black')
        self._notify_change()
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable the widget
        
        Args:
            enabled: Whether to enable the widget
        """
        state = "readonly" if enabled else "disabled"
        self.template_combo.config(state=state)
        
        button_state = "normal" if enabled else "disabled"
        self.refresh_button.config(state=button_state)
    
    def get_available_templates(self) -> List[ReportTemplate]:
        """
        Get list of available templates
        
        Returns:
            List of available templates
        """
        return list(self.templates.values())
    
    def get_template_by_name(self, name: str) -> Optional[ReportTemplate]:
        """
        Get template by name
        
        Args:
            name: Template name
            
        Returns:
            Template or None if not found
        """
        for template in self.templates.values():
            if template.name == name:
                return template
        return None
    
    def validate_selection(self) -> bool:
        """
        Validate current selection
        
        Returns:
            True if selection is valid
        """
        if not self.selected_template:
            return False
        
        return self.selected_template.is_valid()
    
    def get_selection_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about current selection
        
        Returns:
            Selection information dictionary or None
        """
        if not self.selected_template:
            return None
        
        return {
            'template': self.selected_template,
            'name': self.selected_template.name,
            'version': self.selected_template.version,
            'description': self.selected_template.description,
            'supported_formats': self.selected_template.get_supported_formats(),
            'supports_multi_estate': self.selected_template.supports_multi_estate(),
            'required_parameters': self.selected_template.get_required_parameters(),
            'is_valid': self.selected_template.is_valid()
        }
    
    def _notify_change(self):
        """Notify change callback"""
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass  # Ignore callback errors
    
    def get_template_preview(self) -> Optional[str]:
        """
        Get template preview text
        
        Returns:
            Preview text or None
        """
        if not self.selected_template:
            return None
        
        preview_parts = []
        
        # Basic info
        preview_parts.append(f"Template: {self.selected_template.name}")
        preview_parts.append(f"Versi: {self.selected_template.version}")
        
        # Description
        if self.selected_template.description:
            preview_parts.append(f"Deskripsi: {self.selected_template.description}")
        
        # Supported formats
        formats = self.selected_template.get_supported_formats()
        if formats:
            preview_parts.append(f"Format: {', '.join(formats)}")
        
        # Multi-estate support
        multi_estate = "Ya" if self.selected_template.supports_multi_estate() else "Tidak"
        preview_parts.append(f"Multi-Estate: {multi_estate}")
        
        # Required parameters
        params = self.selected_template.get_required_parameters()
        if params:
            preview_parts.append(f"Parameter: {', '.join(params)}")
        
        return "\n".join(preview_parts)