"""
Date Range Widget
GUI component for selecting date ranges
"""

import tkinter as tk
from tkinter import ttk
from datetime import date, datetime, timedelta
from typing import Callable, Optional, Tuple
from tkcalendar import DateEntry


class DateRangeWidget:
    """
    Widget for selecting date ranges with validation
    """

    def __init__(self, parent_frame, on_date_changed: Optional[Callable] = None):
        """
        Initialize date range widget

        :param parent_frame: Parent tkinter frame
        :param on_date_changed: Callback when date range changes
        """
        self.parent = parent_frame
        self.on_date_changed = on_date_changed

        self.setup_ui()
        self.set_default_dates()

    def setup_ui(self):
        """Setup the date range UI components"""
        # Main container
        main_container = ttk.LabelFrame(
            self.parent,
            text="Rentang Tanggal",
            padding="10"
        )
        main_container.pack(fill=tk.X, pady=5)

        # Date input fields
        date_frame = ttk.Frame(main_container)
        date_frame.pack(fill=tk.X)

        # Start date
        ttk.Label(date_frame, text="Tanggal Mulai:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.start_date = DateEntry(
            date_frame,
            width=20,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.start_date.grid(row=0, column=1, padx=(0, 20), pady=5)

        # End date
        ttk.Label(date_frame, text="Tanggal Akhir:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.end_date = DateEntry(
            date_frame,
            width=20,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.end_date.grid(row=0, column=3, padx=(0, 0), pady=5)

        # Bind date change events
        self.start_date.bind("<<DateEntrySelected>>", self._on_date_changed)
        self.end_date.bind("<<DateEntrySelected>>", self._on_date_changed)

        # Quick selection buttons
        quick_frame = ttk.Frame(main_container)
        quick_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(quick_frame, text="Quick Selection:").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            quick_frame,
            text="Bulan Ini",
            command=self.select_current_month
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            quick_frame,
            text="Bulan Lalu",
            command=self.select_last_month
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            quick_frame,
            text="3 Bulan Terakhir",
            command=self.select_last_3_months
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            quick_frame,
            text="6 Bulan Terakhir",
            command=self.select_last_6_months
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            quick_frame,
            text="Tahun Ini",
            command=self.select_current_year
        ).pack(side=tk.LEFT, padx=2)

        # Custom range button
        ttk.Button(
            quick_frame,
            text="Custom Range...",
            command=self.open_custom_range_dialog
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Status label
        self.status_label = ttk.Label(
            main_container,
            text="Status: Ready",
            foreground="green"
        )
        self.status_label.pack(pady=(5, 0))

    def set_default_dates(self):
        """Set default date range (current month)"""
        self.select_current_month()

    def select_current_month(self):
        """Select current month"""
        today = date.today()
        first_day = today.replace(day=1)

        # Find last day of current month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        last_day = next_month - timedelta(days=1)

        self.start_date.set_date(first_day)
        self.end_date.set_date(last_day)

    def select_last_month(self):
        """Select last month"""
        today = date.today()
        if today.month == 1:
            last_month = today.replace(year=today.year - 1, month=12, day=1)
        else:
            last_month = today.replace(month=today.month - 1, day=1)

        # Find last day of last month
        if last_month.month == 12:
            next_month = last_month.replace(year=last_month.year + 1, month=1, day=1)
        else:
            next_month = last_month.replace(month=last_month.month + 1, day=1)

        last_day = next_month - timedelta(days=1)

        self.start_date.set_date(last_month)
        self.end_date.set_date(last_day)

    def select_last_3_months(self):
        """Select last 3 months"""
        today = date.today()
        end_day = today.replace(day=1) - timedelta(days=1)  # Last day of previous month

        # Calculate start date (3 months ago)
        if end_day.month <= 3:
            start_year = end_day.year - 1
            start_month = end_day.month + 9
        else:
            start_year = end_day.year
            start_month = end_day.month - 3

        start_day = date(start_year, start_month, 1)

        self.start_date.set_date(start_day)
        self.end_date.set_date(end_day)

    def select_last_6_months(self):
        """Select last 6 months"""
        today = date.today()
        end_day = today.replace(day=1) - timedelta(days=1)  # Last day of previous month

        # Calculate start date (6 months ago)
        if end_day.month <= 6:
            start_year = end_day.year - 1
            start_month = end_day.month + 6
        else:
            start_year = end_day.year
            start_month = end_day.month - 6

        start_day = date(start_year, start_month, 1)

        self.start_date.set_date(start_day)
        self.end_date.set_date(end_day)

    def select_current_year(self):
        """Select current year"""
        today = date.today()
        start_day = date(today.year, 1, 1)
        end_day = date(today.year, 12, 31)

        self.start_date.set_date(start_day)
        self.end_date.set_date(end_day)

    def open_custom_range_dialog(self):
        """Open custom range selection dialog"""
        dialog = CustomRangeDialog(self.parent, self)
        dialog.show()

    def get_date_range(self) -> Tuple[date, date]:
        """
        Get selected date range

        :return: Tuple of (start_date, end_date)
        """
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        return start_date, end_date

    def get_date_range_string(self) -> str:
        """
        Get date range as formatted string

        :return: Formatted date range string
        """
        start_date, end_date = self.get_date_range()
        return f"{start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}"

    def get_days_count(self) -> int:
        """
        Get number of days in selected range

        :return: Number of days
        """
        start_date, end_date = self.get_date_range()
        return (end_date - start_date).days + 1

    def validate_date_range(self) -> bool:
        """
        Validate selected date range

        :return: True if valid
        """
        start_date, end_date = self.get_date_range()

        if start_date > end_date:
            self.update_status("Error: Tanggal mulai tidak boleh setelah tanggal akhir", "red")
            return False

        # Check if date range is too large
        days = self.get_days_count()
        if days > 365:
            self.update_status(f"Warning: Range besar ({days} hari)", "orange")
        else:
            self.update_status(f"Range valid ({days} hari)", "green")

        # Check if dates are in future
        today = date.today()
        if end_date > today:
            self.update_status("Warning: Tanggal akhir di masa depan", "orange")

        return True

    def set_date_range(self, start_date: date, end_date: date):
        """
        Set specific date range

        :param start_date: Start date
        :param end_date: End date
        """
        self.start_date.set_date(start_date)
        self.end_date.set_date(end_date)
        self._on_date_changed()

    def _on_date_changed(self, event=None):
        """Handle date change event"""
        try:
            if self.validate_date_range():
                if self.on_date_changed:
                    self.on_date_changed()
        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def update_status(self, message: str, color: str = "black"):
        """Update status label"""
        self.status_label.config(text=f"Status: {message}", foreground=color)

    def enable_date_selection(self, enabled: bool = True):
        """Enable or disable date selection"""
        state = 'normal' if enabled else 'disabled'
        self.start_date.set_state(state)
        self.end_date.set_state(state)

    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)


class CustomRangeDialog:
    """Dialog for custom date range selection"""

    def __init__(self, parent, date_widget: DateRangeWidget):
        self.parent = parent
        self.date_widget = date_widget

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Custom Date Range")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.center_dialog()

    def setup_ui(self):
        """Setup dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Pilih rentang tanggal kustom untuk analisis",
            font=('Arial', 10, 'bold')
        )
        instructions.pack(pady=(0, 20))

        # Date selection
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=10)

        # Start date
        ttk.Label(date_frame, text="Dari Tanggal:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        start_entry = ttk.Entry(date_frame, textvariable=self.start_date_var, width=20)
        start_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # End date
        ttk.Label(date_frame, text="Sampai Tanggal:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        end_entry = ttk.Entry(date_frame, textvariable=self.end_date_var, width=20)
        end_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Calendar selection buttons
        calendar_frame = ttk.Frame(main_frame)
        calendar_frame.pack(fill=tk.X, pady=10)

        ttk.Label(calendar_frame, text="Pilih dari kalender:").pack(anchor=tk.W)

        button_frame = ttk.Frame(calendar_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Pilih Tanggal Mulai",
            command=lambda: self.select_date('start')
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Pilih Tanggal Akhir",
            command=lambda: self.select_date('end')
        ).pack(side=tk.LEFT, padx=5)

        # Preset options
        preset_frame = ttk.LabelFrame(main_frame, text="Opsi Preset", padding="10")
        preset_frame.pack(fill=tk.X, pady=10)

        presets = [
            ("7 Hari Terakhir", self.select_last_7_days),
            ("30 Hari Terakhir", self.select_last_30_days),
            ("90 Hari Terakhir", self.select_last_90_days),
            ("YTD (Year to Date)", self.select_ytd),
            ("Kuartal 1", lambda: self.select_quarter(1)),
            ("Kuartal 2", lambda: self.select_quarter(2)),
            ("Kuartal 3", lambda: self.select_quarter(3)),
            ("Kuartal 4", lambda: self.select_quarter(4))
        ]

        for i, (text, command) in enumerate(presets):
            ttk.Button(
                preset_frame,
                text=text,
                command=command
            ).grid(row=i//2, column=i%2, sticky=tk.W, pady=2, padx=5)

        # Current selection display
        self.selection_label = ttk.Label(
            main_frame,
            text="Pilihan saat ini: -",
            font=('Arial', 9),
            foreground='blue'
        )
        self.selection_label.pack(pady=10)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Terapkan", command=self.apply_range).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Batal", command=self.cancel).pack(side=tk.LEFT, padx=5)

        # Initialize with current dates
        current_start, current_end = self.date_widget.get_date_range()
        self.start_date_var.set(current_start.strftime('%Y-%m-%d'))
        self.end_date_var.set(current_end.strftime('%Y-%m-%d'))
        self.update_selection_display()

    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def select_date(self, field: str):
        """Open date selection dialog"""
        from tkcalendar import Calendar

        # Create simple calendar dialog
        cal_dialog = tk.Toplevel(self.dialog)
        cal_dialog.title(f"Pilih Tanggal {'Mulai' if field == 'start' else 'Akhir'}")
        cal_dialog.geometry("300x250")

        cal = Calendar(cal_dialog, selectmode='day')
        cal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def on_date_selected():
            selected_date = cal.selection_get()
            formatted_date = selected_date.strftime('%Y-%m-%d')

            if field == 'start':
                self.start_date_var.set(formatted_date)
            else:
                self.end_date_var.set(formatted_date)

            self.update_selection_display()
            cal_dialog.destroy()

        ttk.Button(
            cal_dialog,
            text="Pilih",
            command=on_date_selected
        ).pack(pady=5)

    def select_last_7_days(self):
        """Select last 7 days"""
        today = date.today()
        start_date = today - timedelta(days=6)
        end_date = today

        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        self.update_selection_display()

    def select_last_30_days(self):
        """Select last 30 days"""
        today = date.today()
        start_date = today - timedelta(days=29)
        end_date = today

        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        self.update_selection_display()

    def select_last_90_days(self):
        """Select last 90 days"""
        today = date.today()
        start_date = today - timedelta(days=89)
        end_date = today

        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        self.update_selection_display()

    def select_ytd(self):
        """Select year to date"""
        today = date.today()
        start_date = date(today.year, 1, 1)
        end_date = today

        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        self.update_selection_display()

    def select_quarter(self, quarter: int):
        """Select specific quarter"""
        today = date.today()
        current_year = today.year

        quarter_starts = [
            date(current_year, 1, 1),
            date(current_year, 4, 1),
            date(current_year, 7, 1),
            date(current_year, 10, 1)
        ]

        quarter_ends = [
            date(current_year, 3, 31),
            date(current_year, 6, 30),
            date(current_year, 9, 30),
            date(current_year, 12, 31)
        ]

        start_date = quarter_starts[quarter - 1]
        end_date = quarter_ends[quarter - 1]

        # If end date is in future, use today instead
        if end_date > today:
            end_date = today

        self.start_date_var.set(start_date.strftime('%Y-%m-%d'))
        self.end_date_var.set(end_date.strftime('%Y-%m-%d'))
        self.update_selection_display()

    def update_selection_display(self):
        """Update selection display"""
        try:
            start_str = self.start_date_var.get()
            end_str = self.end_date_var.get()

            if start_str and end_str:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

                days = (end_date - start_date).days + 1
                formatted_range = f"{start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')} ({days} hari)"

                self.selection_label.config(text=f"Pilihan saat ini: {formatted_range}")
            else:
                self.selection_label.config(text="Pilihan saat ini: -")

        except ValueError:
            self.selection_label.config(text="Pilihan saat ini: Format tanggal tidak valid")

    def apply_range(self):
        """Apply selected date range"""
        try:
            start_str = self.start_date_var.get()
            end_str = self.end_date_var.get()

            if not start_str or not end_str:
                messagebox.showerror("Error", "Harap pilih tanggal mulai dan akhir")
                return

            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

            if start_date > end_date:
                messagebox.showerror("Error", "Tanggal mulai tidak boleh setelah tanggal akhir")
                return

            self.date_widget.set_date_range(start_date, end_date)
            self.dialog.destroy()

        except ValueError:
            messagebox.showerror("Error", "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")

    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()

    def show(self):
        """Show dialog"""
        self.dialog.wait_window()
    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)
        elif hasattr(self, 'parent'):
            # For widgets that don't have main_container, just return
            pass

