"""
Month Selection Widget
Widget for selecting month in YYYY-MM format
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from typing import Optional, Callable
import calendar


class MonthSelectionWidget(ttk.Frame):
    """
    Widget for selecting month in YYYY-MM format
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize month selection widget
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        # Callback for change events
        self.on_change: Optional[Callable] = None
        
        # Current selection
        self._selected_month: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        
        # Set default to current month
        self.set_current_month()
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        
        # Year selection
        year_label = ttk.Label(self, text="Tahun:")
        year_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # Year combobox
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 2)]
        
        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(
            self,
            textvariable=self.year_var,
            values=years,
            state="readonly",
            width=8
        )
        self.year_combo.grid(row=1, column=0, sticky=tk.W+tk.E, padx=(0, 10))
        self.year_combo.bind('<<ComboboxSelected>>', self._on_selection_changed)
        
        # Month selection
        month_label = ttk.Label(self, text="Bulan:")
        month_label.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # Month combobox
        months = [
            ("01", "Januari"),
            ("02", "Februari"),
            ("03", "Maret"),
            ("04", "April"),
            ("05", "Mei"),
            ("06", "Juni"),
            ("07", "Juli"),
            ("08", "Agustus"),
            ("09", "September"),
            ("10", "Oktober"),
            ("11", "November"),
            ("12", "Desember")
        ]
        
        self.month_var = tk.StringVar()
        self.month_combo = ttk.Combobox(
            self,
            textvariable=self.month_var,
            values=[f"{code} - {name}" for code, name in months],
            state="readonly",
            width=15
        )
        self.month_combo.grid(row=1, column=2, sticky=tk.W+tk.E, padx=(10, 0))
        self.month_combo.bind('<<ComboboxSelected>>', self._on_selection_changed)
        
        # Store month mapping
        self.month_mapping = {f"{code} - {name}": code for code, name in months}
        self.reverse_month_mapping = {code: f"{code} - {name}" for code, name in months}
    
    def set_current_month(self):
        """Set selection to current month"""
        now = datetime.now()
        self.year_var.set(str(now.year))
        month_code = f"{now.month:02d}"
        if month_code in self.reverse_month_mapping:
            self.month_var.set(self.reverse_month_mapping[month_code])
        self._update_selected_month()
    
    def get_selected_month(self) -> Optional[str]:
        """
        Get selected month in YYYY-MM format
        
        Returns:
            Selected month string or None if no selection
        """
        return self._selected_month
    
    def set_selected_month(self, month_str: str):
        """
        Set selected month
        
        Args:
            month_str: Month string in YYYY-MM format
        """
        try:
            if not month_str or len(month_str) != 7 or month_str[4] != '-':
                return
            
            year_part = month_str[:4]
            month_part = month_str[5:7]
            
            # Validate year
            if year_part in [self.year_combo.cget('values')[i] for i in range(len(self.year_combo.cget('values')))]:
                self.year_var.set(year_part)
            
            # Validate and set month
            if month_part in self.reverse_month_mapping:
                self.month_var.set(self.reverse_month_mapping[month_part])
            
            self._update_selected_month()
            
        except (ValueError, IndexError):
            pass
    
    def clear_selection(self):
        """Clear current selection"""
        self.year_var.set("")
        self.month_var.set("")
        self._selected_month = None
        self._notify_change()
    
    def set_enabled(self, enabled: bool):
        """
        Enable or disable the widget
        
        Args:
            enabled: Whether to enable the widget
        """
        state = "readonly" if enabled else "disabled"
        self.year_combo.config(state=state)
        self.month_combo.config(state=state)
    
    def _on_selection_changed(self, event=None):
        """Handle selection change"""
        self._update_selected_month()
        self._notify_change()
    
    def _update_selected_month(self):
        """Update selected month string"""
        year = self.year_var.get()
        month_display = self.month_var.get()
        
        if year and month_display and month_display in self.month_mapping:
            month_code = self.month_mapping[month_display]
            self._selected_month = f"{year}-{month_code}"
        else:
            self._selected_month = None
    
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
            True if selection is valid
        """
        if not self._selected_month:
            return False
        
        try:
            # Parse and validate date
            year, month = self._selected_month.split('-')
            year_int = int(year)
            month_int = int(month)
            
            # Check ranges
            if not (2000 <= year_int <= 2030):
                return False
            
            if not (1 <= month_int <= 12):
                return False
            
            # Check if month is not in the future
            now = datetime.now()
            selected_date = date(year_int, month_int, 1)
            current_month = date(now.year, now.month, 1)
            
            return selected_date <= current_month
            
        except (ValueError, TypeError):
            return False
    
    def get_month_info(self) -> Optional[dict]:
        """
        Get information about selected month
        
        Returns:
            Dictionary with month information or None
        """
        if not self._selected_month:
            return None
        
        try:
            year, month = self._selected_month.split('-')
            year_int = int(year)
            month_int = int(month)
            
            # Get month name
            month_names = [
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ]
            
            # Get days in month
            days_in_month = calendar.monthrange(year_int, month_int)[1]
            
            # Get first and last day
            first_day = date(year_int, month_int, 1)
            last_day = date(year_int, month_int, days_in_month)
            
            return {
                'year': year_int,
                'month': month_int,
                'month_name': month_names[month_int - 1],
                'days_in_month': days_in_month,
                'first_day': first_day,
                'last_day': last_day,
                'formatted': self._selected_month
            }
            
        except (ValueError, IndexError):
            return None