#!/usr/bin/env python3
"""
GUI Components for FFB Analysis System
Modular UI components for improved maintainability.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import date


class EstateConfigFrame:
    """Frame for estate configuration and selection."""

    def __init__(self, parent, estate_config):
        """
        Initialize estate configuration frame.

        Args:
            parent: Parent tkinter widget
            estate_config: EstateConfig instance
        """
        self.parent = parent
        self.estate_config = estate_config
        self.estates = {}

        # Create frame
        self.frame = ttk.LabelFrame(parent, text="Konfigurasi Database Estate", padding="10")

        # Estate tree widget
        tree_frame = ttk.Frame(self.frame)
        tree_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        # Create treeview for estate display
        columns = ('estate', 'path', 'status')
        self.estate_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=8
        )

        # Configure columns
        self.estate_tree.heading('estate', text='Estate')
        self.estate_tree.heading('path', text='Path Database')
        self.estate_tree.heading('status', text='Status')

        self.estate_tree.column('estate', width=120, anchor=tk.W)
        self.estate_tree.column('path', width=400, anchor=tk.W)
        self.estate_tree.column('status', width=80, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.estate_tree.yview)
        self.estate_tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.estate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons
        self._create_control_buttons()

        # Populate tree
        self.refresh_estate_display()

    def _create_control_buttons(self):
        """Create control buttons for estate management."""
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)

        ttk.Button(
            button_frame,
            text="Pilih Semua",
            command=self.select_all_estates
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Hapus Pilihan",
            command=self.clear_estate_selection
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Ubah Path...",
            command=self.change_estate_path
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Test Koneksi",
            command=self.test_connections
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Simpan Konfigurasi",
            command=self.save_configuration
        ).pack(side=tk.LEFT, padx=5)

    def refresh_estate_display(self):
        """Refresh the estate tree display with current data."""
        # Clear existing items
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)

        # Add estates
        for estate_name, db_path in self.estates.items():
            status = "✓ Tersedia" if os.path.exists(db_path) else "✗ Tidak Ditemukan"
            self.estate_tree.insert('', tk.END, values=(estate_name, db_path, status))

    def load_estates(self, estates):
        """
        Load estate data into the tree.

        Args:
            estates: Dictionary of estate configurations
        """
        self.estates = estates.copy()
        self.refresh_estate_display()

    def get_selected_estates(self) -> list:
        """
        Get list of currently selected estates.

        Returns:
            List of selected estate names
        """
        selected_items = self.estate_tree.selection()
        return [self.estate_tree.item(item)['values'][0] for item in selected_items]

    def select_all_estates(self):
        """Select all estates in the tree."""
        for item in self.estate_tree.get_children():
            self.estate_tree.selection_add(item)

    def clear_estate_selection(self):
        """Clear all estate selections."""
        self.estate_tree.selection_remove(self.estate_tree.selection())

    def change_estate_path(self):
        """Change database path for selected estate."""
        selected_item = self.estate_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Silakan pilih satu estate untuk diubah path-nya.")
            return

        item_values = self.estate_tree.item(selected_item)['values']
        estate_name = item_values[0]
        current_path = item_values[1]

        new_path = filedialog.askopenfilename(
            title=f"Pilih Database untuk {estate_name}",
            filetypes=[("Firebird Database", "*.fdb")],
            initialdir=os.path.dirname(current_path)
        )

        if new_path:
            self.estates[estate_name] = new_path
            self.refresh_estate_display()
            messagebox.showinfo("Info", f"Path untuk {estate_name} telah diubah.")

    def test_connections(self):
        """Test database connections for all estates."""
        try:
            from core.database import DatabaseManager
        except ImportError:
            messagebox.showerror("Import Error", "Tidak dapat import module database")
            return

        # Create temporary database manager for testing
        test_manager = DatabaseManager(self.estates)
        results = test_manager.test_all_connections()

        # Show results
        result_text = "HASIL TEST KONEKSI:\n\n"
        for estate_name, is_connected in results.items():
            status = "✓ BERHASIL" if is_connected else "✗ GAGAL"
            result_text += f"{estate_name}: {status}\n"

        messagebox.showinfo("Test Koneksi", result_text)

    def save_configuration(self):
        """Save current estate configuration."""
        self.estate_config.estates = self.estates
        self.estate_config.save_config()


class DateRangeFrame:
    """Frame for date range selection."""

    def __init__(self, parent):
        """
        Initialize date range frame.

        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent

        # Create frame
        self.frame = ttk.LabelFrame(parent, text="Rentang Tanggal", padding="10")

        # Date selection widgets
        ttk.Label(self.frame, text="Tanggal Mulai:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date = DateEntry(self.frame, width=20, background='darkblue', foreground='white')
        self.start_date.grid(row=0, column=1, padx=(10, 0), pady=5)

        ttk.Label(self.frame, text="Tanggal Akhir:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.end_date = DateEntry(self.frame, width=20, background='darkblue', foreground='white')
        self.end_date.grid(row=0, column=3, padx=(10, 0), pady=5)

        # Quick select buttons
        self._create_quick_select_buttons()

        # Set default dates
        self.set_default_dates()

    def _create_quick_select_buttons(self):
        """Create quick date selection buttons."""
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)

        ttk.Label(button_frame, text="Quick Select:").pack(side=tk.LEFT, padx=5)

        # Quick select options
        quick_options = [
            ("Bulan Ini", self.set_current_month),
            ("30 Hari Terakhir", self.set_last_30_days),
            ("3 Bulan Terakhir", self.set_last_3_months),
            ("Reset ke Default", self.set_default_dates)
        ]

        for text, command in quick_options:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)

    def set_default_dates(self):
        """Set default date range."""
        self.start_date.set_date(date(2025, 5, 1))
        self.end_date.set_date(date(2025, 5, 31))

    def set_current_month(self):
        """Set date range to current month."""
        today = date.today()
        first_day = today.replace(day=1)
        self.start_date.set_date(first_day)
        self.end_date.set_date(today)

    def set_last_30_days(self):
        """Set date range to last 30 days."""
        today = date.today()
        start_date = today.replace(day=today.day - 30)
        self.start_date.set_date(start_date)
        self.end_date.set_date(today)

    def set_last_3_months(self):
        """Set date range to last 3 months."""
        today = date.today()
        if today.month > 3:
            start_date = today.replace(month=today.month - 3)
        else:
            start_date = today.replace(year=today.year - 1, month=today.month + 9)

        self.start_date.set_date(start_date)
        self.end_date.set_date(today)

    def get_start_date(self) -> date:
        """Get selected start date."""
        return self.start_date.get_date()

    def get_end_date(self) -> date:
        """Get selected end date."""
        return self.end_date.get_date()


class ProgressFrame:
    """Frame for progress display."""

    def __init__(self, parent):
        """
        Initialize progress frame.

        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent

        # Create frame
        self.frame = ttk.LabelFrame(parent, text="Progress", padding="10")

        # Status label
        ttk.Label(self.frame, text="Status:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="Siap untuk menganalisis")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Progress bar
        ttk.Label(self.frame, text="Progress:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.progress_bar = ttk.Progressbar(self.frame, mode='determinate')
        self.progress_bar.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)

    def set_status(self, status_text):
        """Update status text."""
        self.status_var.set(status_text)
        self.parent.update_idletasks()

    def set_progress(self, current, maximum):
        """Update progress bar."""
        self.progress_bar['maximum'] = maximum
        self.progress_bar['value'] = current
        self.parent.update_idletasks()


class ResultsFrame:
    """Frame for displaying analysis results and logs."""

    def __init__(self, parent):
        """
        Initialize results frame.

        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent

        # Create frame
        self.frame = ttk.LabelFrame(parent, text="Log Analisis", padding="10")

        # Text widget for results
        text_frame = ttk.Frame(self.frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.results_text = tk.Text(text_frame, height=12, width=80, wrap=tk.WORD)
        results_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)

        # Pack text and scrollbar
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons
        self._create_control_buttons()

    def _create_control_buttons(self):
        """Create control buttons for results management."""
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(
            button_frame,
            text="Hapus Log",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Simpan Log",
            command=self.save_results
        ).pack(side=tk.LEFT, padx=5)

    def log_message(self, message):
        """Add a message to the results display.

        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.parent.update_idletasks()

    def clear_results(self):
        """Clear all results from the display."""
        self.results_text.delete(1.0, tk.END)

    def save_results(self):
        """Save results to a text file."""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"analisis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Info", f"Log berhasil disimpan ke {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan log: {str(e)}")


class ButtonFrame:
    """Frame for main action buttons."""

    def __init__(self, parent):
        """
        Initialize button frame.

        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent
        self.on_analysis_complete = None

        # Create frame
        self.frame = ttk.Frame(parent)

        # Main action buttons
        self._create_main_buttons()
        self._create_utility_buttons()

    def _create_main_buttons(self):
        """Create main action buttons."""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            main_frame,
            text="▶ MULAI ANALISIS MULTI-ESTATE",
            command=self.on_start_analysis
        ).pack(pady=5)

        ttk.Button(
            main_frame,
            text="🗑 HAPUS LOG",
            command=self.on_clear_results
        ).pack(pady=5)

    def _create_utility_buttons(self):
        """Create utility buttons."""
        util_frame = ttk.Frame(self.frame)
        util_frame.pack(side=tk.LEFT, padx=20)

        ttk.Button(
            util_frame,
            text="📁 BUKA FOLDER OUTPUT",
            command=self.on_open_output_folder
        ).pack(pady=5)

        ttk.Button(
            util_frame,
            text="ℹ️ TENTANG",
            command=self.on_about
        ).pack(pady=5)

        ttk.Button(
            util_frame,
            text="🚪 KELUAR",
            command=self.on_exit
        ).pack(pady=5)

    def set_callbacks(self, start_analysis_callback, clear_results_callback,
                    open_folder_callback, about_callback, exit_callback):
        """
        Set callback functions for button events.

        Args:
            start_analysis_callback: Function to call when analysis starts
            clear_results_callback: Function to call when clearing results
            open_folder_callback: Function to call when opening output folder
            about_callback: Function to call when showing about dialog
            exit_callback: Function to call when exiting application
        """
        self.on_start_analysis = start_analysis_callback
        self.on_clear_results = clear_results_callback
        self.on_open_output_folder = open_folder_callback
        self.on_about = about_callback
        self.on_exit = exit_callback

    def enable_buttons(self, enabled=True):
        """Enable or disable all buttons."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for widget in self.frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.configure(state=state)

    def on_start_analysis(self):
        """Handle start analysis button click."""
        if self.on_start_analysis:
            self.on_start_analysis()

    def on_clear_results(self):
        """Handle clear results button click."""
        if self.on_clear_results:
            self.on_clear_results()

    def on_open_output_folder(self):
        """Handle open output folder button click."""
        if self.on_open_output_folder:
            self.on_open_output_folder()

    def on_about(self):
        """Handle about button click."""
        if self.on_about:
            self.on_about()

    def on_exit(self):
        """Handle exit button click."""
        if self.on_exit:
            self.on_exit()