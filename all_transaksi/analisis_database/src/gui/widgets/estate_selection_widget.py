"""
Estate Selection Widget
GUI component for selecting and configuring estates
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Callable, Optional, Tuple
from services.simple_configuration_service import SimpleConfigurationService
from services.validation_service import ValidationService


class EstateSelectionWidget:
    """
    Widget for estate selection and configuration management
    """

    def __init__(self, parent_frame, config_service: SimpleConfigurationService,
                 validation_service: Optional[ValidationService] = None,
                 on_selection_changed: Optional[Callable] = None):
        """
        Initialize estate selection widget

        :param parent_frame: Parent tkinter frame
        :param config_service: Configuration service instance
        :param validation_service: Optional validation service
        :param on_selection_changed: Callback when selection changes
        """
        self.parent = parent_frame
        self.config_service = config_service
        self.validation_service = validation_service or ValidationService()
        self.on_selection_changed = on_selection_changed

        self.setup_ui()
        self.load_estates()

    def setup_ui(self):
        """Setup the estate selection UI components"""
        # Main container
        self.main_container = ttk.LabelFrame(
            self.parent,
            text="Konfigurasi Database Estate",
            padding="10"
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview for estate display
        tree_frame = ttk.Frame(self.main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create Treeview with columns
        self.estate_tree = ttk.Treeview(
            tree_frame,
            columns=('estate', 'path', 'status'),
            show='headings',
            height=8
        )

        # Configure columns
        self.estate_tree.heading('estate', text='Estate')
        self.estate_tree.heading('path', text='Path Database')
        self.estate_tree.heading('status', text='Status')

        self.estate_tree.column('estate', width=150, anchor=tk.W)
        self.estate_tree.column('path', width=400, anchor=tk.W)
        self.estate_tree.column('status', width=100, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.estate_tree.yview)
        self.estate_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.estate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.estate_tree.bind('<<TreeviewSelect>>', self._on_selection_changed)

        # Control buttons frame
        button_frame = ttk.Frame(self.main_container)
        button_frame.pack(fill=tk.X, pady=10)

        # Selection buttons
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
            text="Ubah Path",
            command=self.change_estate_path
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Tambah Estate",
            command=self.add_estate
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Hapus Estate",
            command=self.remove_estate
        ).pack(side=tk.LEFT, padx=5)

        # Configuration buttons frame
        config_frame = ttk.Frame(self.main_container)
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            config_frame,
            text="Simpan Konfigurasi",
            command=self.save_configuration
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            config_frame,
            text="Validasi Semua",
            command=self.validate_all_estates
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            config_frame,
            text="Backup Config",
            command=self.backup_configuration
        ).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = ttk.Label(
            self.main_container,
            text="Status: Siap",
            foreground="green"
        )
        self.status_label.pack(pady=5)

    def load_estates(self):
        """Load estates from configuration service"""
        try:
            self.estates = self.config_service.get_estate_objects()
            self.populate_estate_tree()
            self.update_status("Estate berhasil dimuat", "green")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat estate: {e}")
            self.update_status("Error memuat estate", "red")

    def populate_estate_tree(self):
        """Populate treeview with estate data"""
        # Clear existing items
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)

        # Add estates to treeview
        for estate_name, estate in self.estates.items():
            status = "✓ Terhubung" if estate.is_connected else "✗ Tidak Terhubung"

            item_id = self.estate_tree.insert(
                '',
                tk.END,
                values=(estate_name, estate.database_path, status)
            )

            # Color code based on connection status
            if estate.is_connected:
                self.estate_tree.set(item_id, 'tags', ('connected',))
            else:
                self.estate_tree.set(item_id, 'tags', ('disconnected',))

        # Configure tags for colors
        self.estate_tree.tag_configure('connected', foreground='green')
        self.estate_tree.tag_configure('disconnected', foreground='red')

    def get_selected_estates(self) -> List[Tuple[str, str]]:
        """
        Get selected estates

        :return: List of (estate_name, database_path) tuples
        """
        selected_items = self.estate_tree.selection()
        selected_estates = []

        for item_id in selected_items:
            values = self.estate_tree.item(item_id, 'values')
            estate_name = values[0]
            db_path = values[1]
            selected_estates.append((estate_name, db_path))

        return selected_estates

    def get_valid_selected_estates(self) -> List[Tuple[str, str]]:
        """
        Get only valid selected estates

        :return: List of valid (estate_name, database_path) tuples
        """
        selected = self.get_selected_estates()
        valid_estates = []

        for estate_name, db_path in selected:
            estate = self.estates.get(estate_name)
            if estate and estate.is_connected:
                valid_estates.append((estate_name, db_path))

        return valid_estates

    def select_all_estates(self):
        """Select all estates in the treeview"""
        for item in self.estate_tree.get_children():
            self.estate_tree.selection_add(item)
        self._on_selection_changed()

    def clear_estate_selection(self):
        """Clear all estate selections"""
        self.estate_tree.selection_remove(self.estate_tree.selection())
        self._on_selection_changed()

    def change_estate_path(self):
        """Change database path for selected estate"""
        selected_items = self.estate_tree.selection()
        if not selected_items:
            messagebox.showwarning("Peringatan", "Silakan pilih satu estate untuk diubah path-nya.")
            return

        if len(selected_items) > 1:
            messagebox.showwarning("Peringatan", "Pilih hanya satu estate untuk diubah path-nya.")
            return

        item_id = selected_items[0]
        values = self.estate_tree.item(item_id, 'values')
        estate_name = values[0]
        current_path = values[1]

        # Open file dialog
        new_path = filedialog.askopenfilename(
            title="Pilih File Database (.FDB)",
            initialdir=current_path if os.path.exists(current_path) else "",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )

        if new_path:
            try:
                # Update configuration
                success = self.config_service.update_estate_path(estate_name, new_path)
                if success:
                    # Update estate object
                    estate = self.estates.get(estate_name)
                    if estate:
                        estate.database_path = new_path
                        estate.is_connected = False
                        estate.connection_error = None

                    # Update treeview
                    self.estate_tree.item(item_id, values=(estate_name, new_path, "✗ Tidak Terhubung"))
                    self.update_status(f"Path {estate_name} berhasil diubah", "green")

                    # Test connection
                    self._test_estate_connection(estate_name)
                else:
                    messagebox.showerror("Error", f"Gagal menyimpan konfigurasi untuk {estate_name}")

            except Exception as e:
                messagebox.showerror("Error", f"Error mengubah path estate: {e}")

    def add_estate(self):
        """Add new estate to configuration"""
        dialog = EstateAddDialog(self.parent, self.config_service)
        if dialog.result:
            estate_name, db_path = dialog.result
            try:
                # Add to configuration
                success = self.config_service.add_estate(estate_name, db_path)
                if success:
                    self.load_estates()
                    self.update_status(f"Estate {estate_name} berhasil ditambahkan", "green")
                else:
                    messagebox.showerror("Error", f"Gagal menambah estate {estate_name}")

            except Exception as e:
                messagebox.showerror("Error", f"Error menambah estate: {e}")

    def remove_estate(self):
        """Remove selected estate from configuration"""
        selected_items = self.estate_tree.selection()
        if not selected_items:
            messagebox.showwarning("Peringatan", "Silakan pilih estate yang akan dihapus.")
            return

        # Get estate names
        estate_names = []
        for item_id in selected_items:
            values = self.estate_tree.item(item_id, 'values')
            estate_names.append(values[0])

        # Confirm deletion
        result = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus {len(estate_names)} estate?\n\n"
            f"Estate: {', '.join(estate_names)}"
        )

        if result:
            try:
                success_count = 0
                for estate_name in estate_names:
                    if self.config_service.remove_estate(estate_name):
                        success_count += 1

                if success_count > 0:
                    self.load_estates()
                    self.update_status(f"{success_count} estate berhasil dihapus", "green")
                else:
                    messagebox.showerror("Error", "Tidak ada estate yang berhasil dihapus")

            except Exception as e:
                messagebox.showerror("Error", f"Error menghapus estate: {e}")

    def save_configuration(self):
        """Save current configuration to file"""
        try:
            # Get current configuration from treeview
            config = {}
            for item in self.estate_tree.get_children():
                values = self.estate_tree.item(item, 'values')
                estate_name = values[0]
                db_path = values[1]
                config[estate_name] = db_path

            success = self.config_service.save_estate_configurations(config)
            if success:
                self.update_status("Konfigurasi berhasil disimpan", "green")
                messagebox.showinfo("Sukses", "Konfigurasi berhasil disimpan ke file")
            else:
                messagebox.showerror("Error", "Gagal menyimpan konfigurasi")

        except Exception as e:
            messagebox.showerror("Error", f"Error menyimpan konfigurasi: {e}")

    def validate_all_estates(self):
        """Validate all estate configurations"""
        try:
            validation_results = self.config_service.validate_all_estates()
            self.show_validation_results(validation_results)

        except Exception as e:
            messagebox.showerror("Error", f"Error validasi estate: {e}")

    def show_validation_results(self, validation_results: Dict[str, Dict[str, Any]]):
        """Show validation results dialog"""
        dialog = ValidationResultsDialog(self.parent, validation_results)
        dialog.show()

    def backup_configuration(self):
        """Backup current configuration"""
        try:
            backup_path = self.config_service.backup_configuration()
            self.update_status(f"Konfigurasi dibackup ke: {backup_path}", "green")
            messagebox.showinfo("Backup Sukses", f"Konfigurasi berhasil dibackup ke:\n{backup_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error backup konfigurasi: {e}")

    def test_connections(self):
        """Test connections for all estates"""
        try:
            results = {}
            for estate_name, estate in self.estates.items():
                self.update_status(f"Menguji koneksi {estate_name}...", "blue")
                success = self._test_estate_connection(estate_name)
                results[estate_name] = success

            # Show summary
            connected = sum(results.values())
            total = len(results)
            self.update_status(f"Koneksi: {connected}/{total} estate terhubung",
                           "green" if connected == total else "orange")

            if connected < total:
                messagebox.showwarning(
                    "Koneksi Tidak Lengkap",
                    f"Hanya {connected} dari {total} estate yang terhubung."
                )

        except Exception as e:
            messagebox.showerror("Error", f"Error testing connections: {e}")

    def _test_estate_connection(self, estate_name: str) -> bool:
        """Test connection for specific estate"""
        estate = self.estates.get(estate_name)
        if not estate:
            return False

        try:
            from repositories.database_repository import DatabaseRepository
            db_repo = DatabaseRepository.create(estate.database_path)
            success = db_repo.test_connection()

            if success:
                estate.mark_connection_success()
            else:
                estate.mark_connection_failure("Connection test failed")

            # Update treeview
            self._update_estate_status(estate_name)

            return success

        except Exception as e:
            estate.mark_connection_failure(str(e))
            self._update_estate_status(estate_name)
            return False

    def _update_estate_status(self, estate_name: str):
        """Update estate status in treeview"""
        for item in self.estate_tree.get_children():
            values = self.estate_tree.item(item, 'values')
            if values[0] == estate_name:
                estate = self.estates.get(estate_name)
                status = "✓ Terhubung" if estate and estate.is_connected else "✗ Tidak Terhubung"
                self.estate_tree.item(item, values=(values[0], values[1], status))

                # Update tags
                if estate and estate.is_connected:
                    self.estate_tree.set(item, 'tags', ('connected',))
                else:
                    self.estate_tree.set(item, 'tags', ('disconnected',))
                break

    def _on_selection_changed(self, event=None):
        """Handle selection change event"""
        if self.on_selection_changed:
            self.on_selection_changed()

        # Update status
        selected_count = len(self.get_selected_estates())
        valid_count = len(self.get_valid_selected_estates())

        if selected_count == 0:
            self.update_status("Tidak ada estate yang dipilih", "orange")
        elif valid_count < selected_count:
            self.update_status(f"{valid_count}/{selected_count} estate valid", "orange")
        else:
            self.update_status(f"{selected_count} estate dipilih dan valid", "green")

    def update_status(self, message: str, color: str = "black"):
        """Update status label"""
        self.status_label.config(text=f"Status: {message}", foreground=color)

    def get_estate_count(self) -> int:
        """Get total number of estates"""
        return len(self.estates)

    def get_selected_count(self) -> int:
        """Get number of selected estates"""
        return len(self.get_selected_estates())

    def get_valid_selected_count(self) -> int:
        """Get number of valid selected estates"""
        return len(self.get_valid_selected_estates())

    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)


class EstateAddDialog:
    """Dialog for adding new estate"""

    def __init__(self, parent, config_service: SimpleConfigurationService):
        self.parent = parent
        self.config_service = config_service
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Tambah Estate Baru")
        self.dialog.geometry("500x300")
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

        # Estate name
        ttk.Label(main_frame, text="Nama Estate:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.estate_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.estate_name_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Database path
        ttk.Label(main_frame, text="Path Database:").grid(row=1, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        self.db_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.db_path_var, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse...", command=self.browse_database).pack(side=tk.RIGHT, padx=(5, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Tambah", command=self.add_estate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Batal", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def browse_database(self):
        """Browse for database file"""
        path = filedialog.askopenfilename(
            title="Pilih File Database (.FDB)",
            filetypes=[("Firebird Database", "*.fdb"), ("All Files", "*.*")]
        )
        if path:
            self.db_path_var.set(path)
            # Auto-suggest estate name from path
            suggested_name = self.config_service.suggest_estate_name(path)
            if suggested_name and not self.estate_name_var.get():
                self.estate_name_var.set(suggested_name)

    def add_estate(self):
        """Add estate"""
        estate_name = self.estate_name_var.get().strip()
        db_path = self.db_path_var.get().strip()

        if not estate_name:
            messagebox.showerror("Error", "Nama estate harus diisi")
            return

        if not db_path:
            messagebox.showerror("Error", "Path database harus diisi")
            return

        # Validate estate name doesn't exist
        existing_estates = self.config_service.load_estate_configurations()
        if estate_name in existing_estates:
            messagebox.showerror("Error", f"Estate '{estate_name}' sudah ada")
            return

        self.result = (estate_name, db_path)
        self.dialog.destroy()

    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class ValidationResultsDialog:
    """Dialog for showing validation results"""

    def __init__(self, parent, validation_results: Dict[str, Dict[str, Any]]):
        self.parent = parent
        self.validation_results = validation_results

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Hasil Validasi Estate")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.center_dialog()

    def setup_ui(self):
        """Setup dialog UI"""
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            width=80,
            height=25
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Close button
        ttk.Button(main_frame, text="Tutup", command=self.close).pack(pady=10)

        # Populate results
        self.populate_results()

    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def populate_results(self):
        """Populate validation results"""
        self.text_widget.insert(tk.END, "HASIL VALIDASI KONFIGURASI ESTATE\n")
        self.text_widget.insert(tk.END, "=" * 50 + "\n\n")

        total_estates = len(self.validation_results)
        valid_estates = sum(1 for result in self.validation_results.values()
                          if result.get('has_fdb', False) and result.get('readable', False))

        self.text_widget.insert(tk.END, f"Total Estate: {total_estates}\n")
        self.text_widget.insert(tk.END, f"Estate Valid: {valid_estates}\n")
        self.text_widget.insert(tk.END, f"Estate Invalid: {total_estates - valid_estates}\n\n")

        for estate_name, result in self.validation_results.items():
            self.text_widget.insert(tk.END, f"Estate: {estate_name}\n")
            self.text_widget.insert(tk.END, f"  Path: {result['path']}\n")
            self.text_widget.insert(tk.END, f"  Status: {result['validation_message']}\n")

            if result.get('errors'):
                self.text_widget.insert(tk.END, "  Errors:\n")
                for error in result['errors']:
                    self.text_widget.insert(tk.END, f"    - {error}\n")

            if result.get('warnings'):
                self.text_widget.insert(tk.END, "  Warnings:\n")
                for warning in result['warnings']:
                    self.text_widget.insert(tk.END, f"    - {warning}\n")

            self.text_widget.insert(tk.END, "\n")

        self.text_widget.config(state=tk.DISABLED)

