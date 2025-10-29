"""
Progress Indicator Widget
Widget for displaying progress during report generation
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
import threading
import time


class ProgressIndicatorWidget(ttk.Frame):
    """
    Widget for displaying progress during operations
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize progress indicator widget
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        # Progress state
        self.is_active = False
        self.current_step = 0
        self.total_steps = 0
        self.current_message = ""
        
        # Callbacks
        self.on_complete: Optional[Callable] = None
        self.on_cancel: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Threading
        self.progress_thread: Optional[threading.Thread] = None
        self.cancel_requested = False
        
        # Setup UI
        self.setup_ui()
        
        # Initially hidden
        self.hide()
    
    def setup_ui(self):
        """Setup user interface"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Main progress frame
        progress_frame = ttk.LabelFrame(self, text="Progress", padding="15")
        progress_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        # Status message
        self.status_label = ttk.Label(
            progress_frame,
            text="Memulai...",
            font=('Arial', 10, 'bold'),
            anchor=tk.W
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(0, 5))
        
        # Progress percentage and step info
        info_frame = ttk.Frame(progress_frame)
        info_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        self.percentage_label = ttk.Label(info_frame, text="0%", font=('Arial', 9))
        self.percentage_label.grid(row=0, column=0, sticky=tk.W)
        
        self.step_label = ttk.Label(info_frame, text="0 / 0", font=('Arial', 9))
        self.step_label.grid(row=0, column=2, sticky=tk.E)
        
        # Detail message (scrollable)
        detail_frame = ttk.Frame(progress_frame)
        detail_frame.grid(row=3, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(0, 10))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        self.detail_text = tk.Text(
            detail_frame,
            height=6,
            wrap=tk.WORD,
            font=('Arial', 9),
            state=tk.DISABLED,
            bg='#f8f8f8'
        )
        self.detail_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Scrollbar for detail text
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        detail_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        # Button frame
        button_frame = ttk.Frame(progress_frame)
        button_frame.grid(row=4, column=0, sticky=tk.W+tk.E)
        
        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Batal",
            command=self.cancel_operation
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Close button (initially hidden)
        self.close_button = ttk.Button(
            button_frame,
            text="Tutup",
            command=self.hide
        )
        
        # Time elapsed
        self.time_label = ttk.Label(button_frame, text="", font=('Arial', 8))
        self.time_label.pack(side=tk.LEFT)
        
        # Start time tracking
        self.start_time = None
        self.time_update_job = None
    
    def start_progress(self, total_steps: int, initial_message: str = "Memulai..."):
        """
        Start progress tracking
        
        Args:
            total_steps: Total number of steps
            initial_message: Initial status message
        """
        self.is_active = True
        self.cancel_requested = False
        self.current_step = 0
        self.total_steps = total_steps
        self.current_message = initial_message
        self.start_time = time.time()
        
        # Reset UI
        self.progress_bar['maximum'] = total_steps
        self.progress_bar['value'] = 0
        self.status_label.config(text=initial_message, foreground='black')
        self.percentage_label.config(text="0%")
        self.step_label.config(text=f"0 / {total_steps}")
        
        # Clear detail text
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.config(state=tk.DISABLED)
        
        # Show cancel button, hide close button
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.close_button.pack_forget()
        
        # Show widget
        self.show()
        
        # Start time update
        self._update_time()
    
    def update_progress(self, step: int, message: str, detail: str = ""):
        """
        Update progress
        
        Args:
            step: Current step number
            message: Status message
            detail: Detailed message
        """
        if not self.is_active:
            return
        
        self.current_step = step
        self.current_message = message
        
        # Update progress bar
        self.progress_bar['value'] = step
        
        # Update labels
        percentage = int((step / self.total_steps) * 100) if self.total_steps > 0 else 0
        self.percentage_label.config(text=f"{percentage}%")
        self.step_label.config(text=f"{step} / {self.total_steps}")
        self.status_label.config(text=message)
        
        # Add detail message
        if detail:
            self._add_detail_message(detail)
        
        # Update display
        self.update_idletasks()
    
    def complete_progress(self, message: str = "Selesai!", detail: str = ""):
        """
        Complete progress
        
        Args:
            message: Completion message
            detail: Detailed completion message
        """
        self.is_active = False
        self.current_step = self.total_steps
        self.current_message = message
        
        # Update UI
        self.progress_bar['value'] = self.total_steps
        self.percentage_label.config(text="100%")
        self.step_label.config(text=f"{self.total_steps} / {self.total_steps}")
        self.status_label.config(text=message, foreground='green')
        
        # Add completion detail
        if detail:
            self._add_detail_message(detail)
        
        # Show close button, hide cancel button
        self.cancel_button.pack_forget()
        self.close_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Stop time update
        if self.time_update_job:
            self.after_cancel(self.time_update_job)
            self.time_update_job = None
        
        # Notify completion
        if self.on_complete:
            try:
                self.on_complete()
            except Exception:
                pass
    
    def error_progress(self, message: str, detail: str = ""):
        """
        Show error in progress
        
        Args:
            message: Error message
            detail: Detailed error message
        """
        self.is_active = False
        self.current_message = message
        
        # Update UI
        self.status_label.config(text=message, foreground='red')
        
        # Add error detail
        if detail:
            self._add_detail_message(f"ERROR: {detail}")
        
        # Show close button, hide cancel button
        self.cancel_button.pack_forget()
        self.close_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Stop time update
        if self.time_update_job:
            self.after_cancel(self.time_update_job)
            self.time_update_job = None
        
        # Notify error
        if self.on_error:
            try:
                self.on_error(message, detail)
            except Exception:
                pass
    
    def cancel_operation(self):
        """Cancel current operation"""
        if not self.is_active:
            return
        
        self.cancel_requested = True
        self.is_active = False
        
        # Update UI
        self.status_label.config(text="Membatalkan...", foreground='orange')
        self.cancel_button.config(state='disabled')
        
        # Add cancellation message
        self._add_detail_message("Operasi dibatalkan oleh pengguna")
        
        # Stop time update
        if self.time_update_job:
            self.after_cancel(self.time_update_job)
            self.time_update_job = None
        
        # Notify cancellation
        if self.on_cancel:
            try:
                self.on_cancel()
            except Exception:
                pass
        
        # Show close button after a delay
        self.after(1000, self._show_close_after_cancel)
    
    def _show_close_after_cancel(self):
        """Show close button after cancellation"""
        self.cancel_button.pack_forget()
        self.close_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.status_label.config(text="Dibatalkan", foreground='red')
    
    def _add_detail_message(self, message: str):
        """
        Add message to detail text
        
        Args:
            message: Message to add
        """
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.insert(tk.END, formatted_message)
        self.detail_text.see(tk.END)
        self.detail_text.config(state=tk.DISABLED)
    
    def _update_time(self):
        """Update elapsed time display"""
        if not self.is_active or not self.start_time:
            return
        
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        time_text = f"Waktu: {minutes:02d}:{seconds:02d}"
        self.time_label.config(text=time_text)
        
        # Schedule next update
        self.time_update_job = self.after(1000, self._update_time)
    
    def show(self):
        """Show the progress widget"""
        self.grid()
    
    def hide(self):
        """Hide the progress widget"""
        self.grid_remove()
        
        # Stop time update
        if self.time_update_job:
            self.after_cancel(self.time_update_job)
            self.time_update_job = None
    
    def is_cancelled(self) -> bool:
        """
        Check if operation was cancelled
        
        Returns:
            True if cancelled
        """
        return self.cancel_requested
    
    def is_running(self) -> bool:
        """
        Check if progress is currently running
        
        Returns:
            True if running
        """
        return self.is_active
    
    def get_progress_info(self) -> Dict[str, Any]:
        """
        Get current progress information
        
        Returns:
            Progress information dictionary
        """
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        percentage = int((self.current_step / self.total_steps) * 100) if self.total_steps > 0 else 0
        
        return {
            'is_active': self.is_active,
            'is_cancelled': self.cancel_requested,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'percentage': percentage,
            'current_message': self.current_message,
            'elapsed_time': elapsed_time
        }
    
    def reset(self):
        """Reset progress widget to initial state"""
        self.is_active = False
        self.cancel_requested = False
        self.current_step = 0
        self.total_steps = 0
        self.current_message = ""
        self.start_time = None
        
        # Reset UI
        self.progress_bar['value'] = 0
        self.status_label.config(text="Siap", foreground='black')
        self.percentage_label.config(text="0%")
        self.step_label.config(text="0 / 0")
        self.time_label.config(text="")
        
        # Clear detail text
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.config(state=tk.DISABLED)
        
        # Reset buttons
        self.cancel_button.config(state='normal')
        self.cancel_button.pack_forget()
        self.close_button.pack_forget()
        
        # Stop time update
        if self.time_update_job:
            self.after_cancel(self.time_update_job)
            self.time_update_job = None
        
        # Hide widget
        self.hide()
    
    def set_indeterminate_mode(self, active: bool = True):
        """
        Set progress bar to indeterminate mode
        
        Args:
            active: Whether to activate indeterminate mode
        """
        if active:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(10)  # Animation speed
            self.percentage_label.config(text="...")
        else:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate')
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """
        Add log message to detail text
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.insert(tk.END, formatted_message)
        self.detail_text.see(tk.END)
        self.detail_text.config(state=tk.DISABLED)
    
    def get_detail_log(self) -> str:
        """
        Get all detail log messages
        
        Returns:
            Complete log text
        """
        return self.detail_text.get(1.0, tk.END).strip()