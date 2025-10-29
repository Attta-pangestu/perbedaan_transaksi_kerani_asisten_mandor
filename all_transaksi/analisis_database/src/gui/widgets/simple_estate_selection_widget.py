"""
Simple Estate Selection Widget
Hanya untuk menampilkan dan memilih estate dengan database path mapping
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Callable, Optional, Tuple
from services.simple_configuration_service import SimpleConfigurationService
from services.validation_service import ValidationService


class SimpleEstateSelectionWidget:
    """
    Simple widget untuk estate selection - hanya mapping estate name -> database path
    """

    def __init__(self, parent_frame, config_service: SimpleConfigurationService,
                 validation_service: Optional[ValidationService] = None,
                 on_selection_changed: Optional[Callable] = None):
        """
        Initialize simple estate selection widget

        :param parent_frame: Parent tkinter frame
        :param config_service: Simple configuration service instance
        :param validation_service: Optional validation service
        :param on_selection_changed: Callback when selection changes
        """
        self.parent = parent_frame
        self.config_service = config_service
        self.validation_service = validation_service or ValidationService()
        self.on_selection_changed = on_selection_changed

        self.selected_estates = set()

        self.setup_ui()
        self.load_estates()

    def setup_ui(self):
        """Setup the simple estate selection UI components"""
        # Main container
        self.main_container = ttk.LabelFrame(
            self.parent,
            text="Pilih Estate untuk Analisis",
            padding="10"
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # Frame untuk estate checkboxes
        estates_frame = ttk.Frame(self.main_container)
        estates_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollable frame untuk checkboxes
        canvas = tk.Canvas(estates_frame, height=200)
        scrollbar = ttk.Scrollbar(estates_frame, orient="vertical", command=canvas.yview)
        self.checkboxes_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.create_window((0, 0), window=self.checkboxes_frame, anchor="nw")
        self.checkboxes_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Control buttons frame
        button_frame = ttk.Frame(self.main_container)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="Pilih Semua",
            command=self.select_all_estates
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Hapus Pilihan",
            command=self.clear_selection
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Refresh Config",
            command=self.refresh_config
        ).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = ttk.Label(
            self.main_container,
            text="Status: Siap",
            foreground="green"
        )
        self.status_label.pack(pady=5)

    def load_estates(self):
        """Load estates dari simple configuration service"""
        try:
            # Clear existing checkboxes
            for widget in self.checkboxes_frame.winfo_children():
                widget.destroy()

            # Get configurations
            estate_configs = self.config_service.get_estate_configurations()

            if not estate_configs:
                self.update_status("Tidak ada estate yang dikonfigurasi", "red")
                return

            # Create checkboxes untuk setiap estate
            self.estate_vars = {}
            self.estate_paths = {}

            for estate_name, db_path in estate_configs.items():
                # Create checkbox
                var = tk.BooleanVar()
                self.estate_vars[estate_name] = var
                self.estate_paths[estate_name] = db_path

                # Check jika file exists
                file_exists = self.config_service.validate_estate_path(db_path)
                status_text = "✓" if file_exists else "✗"
                status_color = "green" if file_exists else "red"

                # Frame untuk checkbox dan info
                estate_frame = ttk.Frame(self.checkboxes_frame)
                estate_frame.pack(fill=tk.X, pady=2, anchor="w")

                # Checkbox
                checkbox = ttk.Checkbutton(
                    estate_frame,
                    text=f"{estate_name}:",
                    variable=var,
                    command=self.on_selection_change
                )
                checkbox.pack(side=tk.LEFT)

                # Path info
                path_label = ttk.Label(
                    estate_frame,
                    text=f"{db_path} {status_text}",
                    foreground=status_color,
                    font=('Arial', 8)
                )
                path_label.pack(side=tk.LEFT, padx=(10, 0))

            self.update_status(f"Loaded {len(estate_configs)} estates", "green")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat estate: {e}")
            self.update_status("Error memuat estate", "red")

    def on_selection_change(self):
        """Handle selection change"""
        # Update selected estates
        self.selected_estates = {
            estate_name for estate_name, var in self.estate_vars.items()
            if var.get()
        }

        # Update status
        selected_count = len(self.selected_estates)
        if selected_count == 0:
            self.update_status("Tidak ada estate yang dipilih", "orange")
        else:
            self.update_status(f"{selected_count} estate dipilih", "green")

        # Call callback
        if self.on_selection_changed:
            self.on_selection_changed()

    def select_all_estates(self):
        """Select all estates"""
        for var in self.estate_vars.values():
            var.set(True)
        self.on_selection_change()

    def clear_selection(self):
        """Clear all estate selections"""
        for var in self.estate_vars.values():
            var.set(False)
        self.on_selection_change()

    def refresh_config(self):
        """Refresh configuration"""
        try:
            self.config_service.reload_configurations()
            self.load_estates()
            self.clear_selection()
            messagebox.showinfo("Info", "Konfigurasi berhasil di-refresh")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal refresh konfigurasi: {e}")

    def get_selected_estates(self) -> List[Tuple[str, str]]:
        """
        Get selected estates

        :return: List of (estate_name, database_path) tuples
        """
        selected = []
        for estate_name in self.selected_estates:
            db_path = self.estate_paths.get(estate_name, "")
            selected.append((estate_name, db_path))
        return selected

    def get_valid_selected_estates(self) -> List[Tuple[str, str]]:
        """
        Get only valid selected estates (dengan database file yang exists)

        :return: List of valid (estate_name, database_path) tuples
        """
        valid_selected = []
        for estate_name, db_path in self.get_selected_estates():
            if self.config_service.validate_estate_path(db_path):
                valid_selected.append((estate_name, db_path))
        return valid_selected

    def get_estate_count(self) -> int:
        """Get total number of estates"""
        return len(self.estate_vars)

    def get_selected_count(self) -> int:
        """Get number of selected estates"""
        return len(self.selected_estates)

    def get_valid_selected_count(self) -> int:
        """Get number of valid selected estates"""
        return len(self.get_valid_selected_estates())

    def update_status(self, message: str, color: str = "black"):
        """Update status label"""
        self.status_label.config(text=f"Status: {message}", foreground=color)

    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)


# Simple usage example
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simple Estate Selection Test")
    root.geometry("600x400")

    # Create simple config service
    from services.simple_configuration_service import SimpleConfigurationService
    config_service = SimpleConfigurationService()

    # Create widget
    widget = SimpleEstateSelectionWidget(root, config_service)
    widget.pack(fill=tk.BOTH, expand=True)

    # Test button
    def show_selection():
        selected = widget.get_selected_estates()
        valid_selected = widget.get_valid_selected_estates()
        print(f"Selected: {selected}")
        print(f"Valid: {valid_selected}")

    ttk.Button(root, text="Show Selection", command=show_selection).pack(pady=10)

    root.mainloop()