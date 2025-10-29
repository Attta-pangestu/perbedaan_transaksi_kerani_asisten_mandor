"""
Progress Widget
GUI component for displaying analysis progress with detailed status tracking
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from typing import Callable, Optional, Dict, Any
from enum import Enum


class ProgressStatus(Enum):
    """Progress status enumeration"""
    IDLE = "idle"
    CONNECTING = "connecting"
    LOADING = "loading"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class ProgressWidget:
    """
    Widget for displaying detailed progress information during analysis
    """

    def __init__(self, parent_frame, on_cancel: Optional[Callable] = None):
        """
        Initialize progress widget

        :param parent_frame: Parent tkinter frame
        :param on_cancel: Optional cancel callback
        """
        self.parent = parent_frame
        self.on_cancel = on_cancel

        # Progress state
        self.current_status = ProgressStatus.IDLE
        self.current_progress = 0
        self.current_operation = ""
        self.start_time = None
        self.elapsed_time = 0
        self.estimated_total_time = 0
        self.cancel_requested = False

        # Progress tracking
        self.operation_progress = {}
        self.sub_operation = ""
        self.sub_progress = 0

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """Setup the progress widget UI"""
        # Main container
        main_container = ttk.LabelFrame(
            self.parent,
            text="Progress Analisis",
            padding="15"
        )
        main_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # Status section
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        # Status label with icon
        self.status_frame_content = ttk.Frame(status_frame)
        self.status_frame_content.pack(fill=tk.X)

        # Status icon
        self.status_icon = ttk.Label(
            self.status_frame_content,
            text="⚪",
            font=('Arial', 16)
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 10))

        # Status text
        self.status_label = ttk.Label(
            self.status_frame_content,
            text="Status: Siap",
            font=('Arial', 11, 'bold')
        )
        self.status_label.pack(side=tk.LEFT)

        # Current operation
        self.operation_label = ttk.Label(
            status_frame,
            text="Menunggu untuk memulai...",
            font=('Arial', 10)
        )
        self.operation_label.pack(fill=tk.X, pady=(5, 0))

        # Progress bars section
        progress_frame = ttk.Frame(main_container)
        progress_frame.pack(fill=tk.X, pady=10)

        # Main progress bar
        ttk.Label(progress_frame, text="Progress Utama:").pack(anchor=tk.W)
        main_progress_container = ttk.Frame(progress_frame)
        main_progress_container.pack(fill=tk.X, pady=(2, 10))

        self.main_progress_bar = ttk.Progressbar(
            main_progress_container,
            mode='determinate',
            length=400
        )
        self.main_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.main_progress_label = ttk.Label(
            main_progress_container,
            text="0%",
            width=6
        )
        self.main_progress_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Sub progress bar (for detailed operations)
        ttk.Label(progress_frame, text="Progress Operasi:").pack(anchor=tk.W)
        sub_progress_container = ttk.Frame(progress_frame)
        sub_progress_container.pack(fill=tk.X, pady=(2, 0))

        self.sub_progress_bar = ttk.Progressbar(
            sub_progress_container,
            mode='determinate',
            length=400
        )
        self.sub_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.sub_progress_label = ttk.Label(
            sub_progress_container,
            text="0%",
            width=6
        )
        self.sub_progress_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Time information section
        time_frame = ttk.Frame(main_container)
        time_frame.pack(fill=tk.X, pady=10)

        # Elapsed time
        elapsed_frame = ttk.Frame(time_frame)
        elapsed_frame.pack(fill=tk.X, pady=2)

        ttk.Label(elapsed_frame, text="Waktu Berjalan:", width=15).pack(side=tk.LEFT)
        self.elapsed_time_label = ttk.Label(
            elapsed_frame,
            text="00:00:00",
            font=('Courier', 10)
        )
        self.elapsed_time_label.pack(side=tk.LEFT)

        # Estimated remaining time
        remaining_frame = ttk.Frame(time_frame)
        remaining_frame.pack(fill=tk.X, pady=2)

        ttk.Label(remaining_frame, text="Perkiraan Sisa:", width=15).pack(side=tk.LEFT)
        self.remaining_time_label = ttk.Label(
            remaining_frame,
            text="--:--:--",
            font=('Courier', 10)
        )
        self.remaining_time_label.pack(side=tk.LEFT)

        # Operations log section
        log_frame = ttk.LabelFrame(main_container, text="Log Operasi", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Log text with scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_container,
            height=8,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(
            log_container,
            orient=tk.VERTICAL,
            command=self.log_text.yview
        )
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        # Configure log text tags for different message types
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("timestamp", foreground="gray")

        # Control buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.cancel_button = ttk.Button(
            button_frame,
            text="Batal",
            command=self.request_cancel,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.clear_log_button = ttk.Button(
            button_frame,
            text="Hapus Log",
            command=self.clear_log
        )
        self.clear_log_button.pack(side=tk.RIGHT, padx=(5, 0))

    def start_progress(self, total_steps: int = 100, operation_name: str = "Analisis"):
        """
        Start progress tracking

        :param total_steps: Total number of steps for main progress
        :param operation_name: Name of the main operation
        """
        self.current_status = ProgressStatus.CONNECTING
        self.current_progress = 0
        self.current_operation = operation_name
        self.start_time = datetime.now()
        self.cancel_requested = False
        self.estimated_total_time = 0

        self.main_progress_bar.config(maximum=total_steps, value=0)
        self.sub_progress_bar.config(maximum=100, value=0)

        self.log_message(f"Memulai {operation_name.lower()}...", "info")
        self.update_display()

        # Start time update thread
        self.start_time_update_thread()

    def update_progress(self, current_step: int, message: str = ""):
        """
        Update main progress

        :param current_step: Current step number
        :param message: Optional status message
        """
        self.current_progress = current_step
        if message:
            self.current_operation = message
            self.log_message(message, "info")

        # Calculate percentage
        total_steps = self.main_progress_bar.cget('maximum')
        percentage = (current_step / total_steps) * 100 if total_steps > 0 else 0

        self.main_progress_bar.config(value=current_step)
        self.main_progress_label.config(text=f"{percentage:.1f}%")

        # Update time estimation
        if self.start_time and current_step > 0:
            self.update_time_estimation(current_step, total_steps)

        self.update_display()

    def update_sub_progress(self, progress: int, sub_operation: str = ""):
        """
        Update sub-operation progress

        :param progress: Sub-operation progress (0-100)
        :param sub_operation: Sub-operation description
        """
        self.sub_progress = progress
        if sub_operation:
            self.sub_operation = sub_operation

        self.sub_progress_bar.config(value=progress)
        self.sub_progress_label.config(text=f"{progress}%")

        self.operation_label.config(
            text=f"{self.current_operation}\n→ {sub_operation}" if sub_operation else self.current_operation
        )

    def set_status(self, status: ProgressStatus, message: str = ""):
        """
        Set current status

        :param status: New status
        :param message: Optional status message
        """
        self.current_status = status
        if message:
            self.log_message(message, self.get_log_type_for_status(status))

        # Update status icon and color
        status_config = {
            ProgressStatus.IDLE: ("⚪", "gray", "Siap"),
            ProgressStatus.CONNECTING: ("🔵", "blue", "Menghubungkan"),
            ProgressStatus.LOADING: ("🟡", "orange", "Memuat Data"),
            ProgressStatus.ANALYZING: ("🟠", "darkorange", "Menganalisis"),
            ProgressStatus.GENERATING: ("🟣", "purple", "Menghasilkan Laporan"),
            ProgressStatus.COMPLETED: ("🟢", "green", "Selesai"),
            ProgressStatus.ERROR: ("🔴", "red", "Error"),
            ProgressStatus.CANCELLED: ("⚫", "black", "Dibatalkan")
        }

        icon, color, text = status_config.get(status, ("⚪", "gray", "Unknown"))
        self.status_icon.config(text=icon, foreground=color)
        self.status_label.config(
            text=f"Status: {text}",
            foreground=color
        )

        # Update cancel button state
        if status in [ProgressStatus.IDLE, ProgressStatus.COMPLETED, ProgressStatus.ERROR, ProgressStatus.CANCELLED]:
            self.cancel_button.config(state=tk.DISABLED)
        else:
            self.cancel_button.config(state=tk.NORMAL)

        self.update_display()

    def complete_progress(self, success_message: str = "Analisis selesai!"):
        """
        Mark progress as completed

        :param success_message: Success message to display
        """
        total_steps = self.main_progress_bar.cget('maximum')
        self.update_progress(total_steps)
        self.update_sub_progress(100, "Selesai")
        self.set_status(ProgressStatus.COMPLETED, success_message)
        self.log_message(success_message, "success")

    def error_progress(self, error_message: str):
        """
        Mark progress as error

        :param error_message: Error message to display
        """
        self.set_status(ProgressStatus.ERROR, f"Error: {error_message}")
        self.log_message(f"ERROR: {error_message}", "error")

    def log_message(self, message: str, message_type: str = "info"):
        """
        Add message to log

        :param message: Message to log
        :param message_type: Type of message (info, success, warning, error)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", message_type)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        """Clear the log text"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def request_cancel(self):
        """Request cancellation of current operation"""
        if not self.cancel_requested:
            self.cancel_requested = True
            self.set_status(ProgressStatus.CANCELLED, "Pembatalan diminta...")
            self.log_message("Pembatalan operasi diminta oleh pengguna", "warning")

            if self.on_cancel:
                self.on_cancel()

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested"""
        return self.cancel_requested

    def start_time_update_thread(self):
        """Start background thread to update elapsed time"""
        def update_time():
            while self.current_status not in [ProgressStatus.COMPLETED, ProgressStatus.ERROR, ProgressStatus.CANCELLED, ProgressStatus.IDLE]:
                if not self.cancel_requested:
                    self.update_elapsed_time()
                time.sleep(1)

        thread = threading.Thread(target=update_time, daemon=True)
        thread.start()

    def update_elapsed_time(self):
        """Update elapsed time display"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            elapsed_str = self.format_duration(elapsed.total_seconds())
            self.elapsed_time_label.config(text=elapsed_str)

    def update_time_estimation(self, current_step: int, total_steps: int):
        """Update estimated remaining time"""
        if self.start_time and current_step > 0:
            elapsed = datetime.now() - self.start_time
            if current_step < total_steps:
                # Estimate total time based on current progress
                estimated_total = elapsed.total_seconds() * (total_steps / current_step)
                remaining_seconds = estimated_total - elapsed.total_seconds()

                if remaining_seconds > 0:
                    remaining_str = self.format_duration(remaining_seconds)
                    self.remaining_time_label.config(text=remaining_str)
                else:
                    self.remaining_time_label.config(text="00:00:00")

    def format_duration(self, seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_log_type_for_status(self, status: ProgressStatus) -> str:
        """Get appropriate log type for status"""
        status_log_mapping = {
            ProgressStatus.IDLE: "info",
            ProgressStatus.CONNECTING: "info",
            ProgressStatus.LOADING: "info",
            ProgressStatus.ANALYZING: "info",
            ProgressStatus.GENERATING: "info",
            ProgressStatus.COMPLETED: "success",
            ProgressStatus.ERROR: "error",
            ProgressStatus.CANCELLED: "warning"
        }
        return status_log_mapping.get(status, "info")

    def update_display(self):
        """Update the overall display"""
        # Update operation label
        if self.sub_operation:
            self.operation_label.config(text=f"{self.current_operation}\n→ {self.sub_operation}")
        else:
            self.operation_label.config(text=self.current_operation)

        # Force GUI update
        self.parent.update_idletasks()

    def reset(self):
        """Reset progress widget to initial state"""
        self.current_status = ProgressStatus.IDLE
        self.current_progress = 0
        self.current_operation = ""
        self.sub_operation = ""
        self.sub_progress = 0
        self.start_time = None
        self.elapsed_time = 0
        self.estimated_total_time = 0
        self.cancel_requested = False

        self.main_progress_bar.config(value=0)
        self.sub_progress_bar.config(value=0)
        self.main_progress_label.config(text="0%")
        self.sub_progress_label.config(text="0%")
        self.elapsed_time_label.config(text="00:00:00")
        self.remaining_time_label.config(text="--:--:--")
        self.operation_label.config(text="Menunggu untuk memulai...")

        self.set_status(ProgressStatus.IDLE)
        self.clear_log()

    def get_current_progress(self) -> Dict[str, Any]:
        """
        Get current progress information

        :return: Dictionary with progress details
        """
        return {
            'status': self.current_status.value,
            'progress': self.current_progress,
            'operation': self.current_operation,
            'sub_operation': self.sub_operation,
            'sub_progress': self.sub_progress,
            'elapsed_time': self.elapsed_time,
            'estimated_total_time': self.estimated_total_time,
            'cancel_requested': self.cancel_requested,
            'start_time': self.start_time.isoformat() if self.start_time else None
        }
    def pack(self, **kwargs):
        """Pack the main container"""
        if hasattr(self, 'main_container'):
            self.main_container.pack(**kwargs)
        elif hasattr(self, 'parent'):
            # For widgets that don't have main_container, just return
            pass

