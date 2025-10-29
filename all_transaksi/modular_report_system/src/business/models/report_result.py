"""
Report Result Model
Model for report generation results
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .report_request import ReportRequest


@dataclass
class ReportResult:
    """
    Model for report generation results
    """
    
    # Required fields
    request: ReportRequest
    start_time: datetime
    
    # Result fields
    success: bool = False
    status: str = "pending"  # pending, in_progress, completed, failed, cancelled
    end_time: Optional[datetime] = None
    
    # Output information
    output_files: Dict[str, str] = field(default_factory=dict)  # format -> file_path
    
    # Error information
    error_message: Optional[str] = None
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    # Progress information
    progress_steps: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    total_steps: int = 6
    
    # Statistics
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.statistics:
            self.statistics = {
                'records_processed': 0,
                'files_generated': 0,
                'data_quality_score': 0.0,
                'processing_time_seconds': 0.0
            }
    
    def get_duration(self) -> Optional[timedelta]:
        """
        Get generation duration
        
        Returns:
            Duration as timedelta, None if not completed
        """
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_duration_seconds(self) -> float:
        """
        Get generation duration in seconds
        
        Returns:
            Duration in seconds, 0.0 if not completed
        """
        duration = self.get_duration()
        return duration.total_seconds() if duration else 0.0
    
    def get_progress_percentage(self) -> float:
        """
        Get progress percentage
        
        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if self.total_steps <= 0:
            return 0.0
        
        if self.status == "completed":
            return 100.0
        elif self.status == "failed" or self.status == "cancelled":
            return 0.0
        
        return min((self.current_step / self.total_steps) * 100.0, 100.0)
    
    def add_progress_step(self, step_number: int, message: str, detail: str = "", 
                         timestamp: Optional[datetime] = None):
        """
        Add progress step
        
        Args:
            step_number: Step number
            message: Progress message
            detail: Detailed message
            timestamp: Step timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        step_info = {
            'step': step_number,
            'message': message,
            'detail': detail,
            'timestamp': timestamp,
            'duration_from_start': (timestamp - self.start_time).total_seconds()
        }
        
        self.progress_steps.append(step_info)
        self.current_step = step_number
    
    def get_current_progress_message(self) -> str:
        """
        Get current progress message
        
        Returns:
            Current progress message
        """
        if not self.progress_steps:
            return "Memulai..."
        
        latest_step = self.progress_steps[-1]
        return latest_step['message']
    
    def get_current_progress_detail(self) -> str:
        """
        Get current progress detail
        
        Returns:
            Current progress detail
        """
        if not self.progress_steps:
            return ""
        
        latest_step = self.progress_steps[-1]
        return latest_step.get('detail', '')
    
    def mark_completed(self, output_files: Dict[str, str] = None):
        """
        Mark result as completed
        
        Args:
            output_files: Generated output files
        """
        self.end_time = datetime.now()
        self.status = "completed"
        self.success = True
        
        if output_files:
            self.output_files = output_files
        
        # Update statistics
        self.statistics['processing_time_seconds'] = self.get_duration_seconds()
        self.statistics['files_generated'] = len(self.output_files)
    
    def mark_failed(self, error_message: str, error_details: Dict[str, Any] = None):
        """
        Mark result as failed
        
        Args:
            error_message: Error message
            error_details: Additional error details
        """
        self.end_time = datetime.now()
        self.status = "failed"
        self.success = False
        self.error_message = error_message
        
        if error_details:
            self.error_details = error_details
        
        # Update statistics
        self.statistics['processing_time_seconds'] = self.get_duration_seconds()
    
    def mark_cancelled(self):
        """Mark result as cancelled"""
        self.end_time = datetime.now()
        self.status = "cancelled"
        self.success = False
        self.error_message = "Generation was cancelled by user"
        
        # Update statistics
        self.statistics['processing_time_seconds'] = self.get_duration_seconds()
    
    def get_output_file_info(self) -> List[Dict[str, Any]]:
        """
        Get information about output files
        
        Returns:
            List of file information dictionaries
        """
        file_info = []
        
        for format_name, file_path in self.output_files.items():
            path_obj = Path(file_path)
            
            info = {
                'format': format_name,
                'file_path': file_path,
                'filename': path_obj.name,
                'directory': str(path_obj.parent),
                'exists': path_obj.exists(),
                'size_bytes': 0,
                'size_human': "0 B"
            }
            
            # Get file size if exists
            if path_obj.exists():
                try:
                    size_bytes = path_obj.stat().st_size
                    info['size_bytes'] = size_bytes
                    info['size_human'] = self._format_file_size(size_bytes)
                except Exception:
                    pass
            
            file_info.append(info)
        
        return file_info
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get result summary
        
        Returns:
            Summary dictionary
        """
        return {
            'request_id': self.request.request_id,
            'template_name': self.request.template.name,
            'status': self.status,
            'success': self.success,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.get_duration_seconds(),
            'progress_percentage': self.get_progress_percentage(),
            'current_message': self.get_current_progress_message(),
            'output_files_count': len(self.output_files),
            'error_message': self.error_message,
            'statistics': self.statistics.copy()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'request': self.request.to_dict(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'success': self.success,
            'status': self.status,
            'output_files': self.output_files,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'progress_steps': [
                {
                    **step,
                    'timestamp': step['timestamp'].isoformat()
                }
                for step in self.progress_steps
            ],
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'statistics': self.statistics,
            'metadata': self.metadata,
            'summary': self.get_summary(),
            'file_info': self.get_output_file_info()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], request: ReportRequest) -> 'ReportResult':
        """
        Create from dictionary
        
        Args:
            data: Dictionary data
            request: Report request
            
        Returns:
            ReportResult instance
        """
        # Parse timestamps
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = None
        if data.get('end_time'):
            end_time = datetime.fromisoformat(data['end_time'])
        
        # Parse progress steps
        progress_steps = []
        for step_data in data.get('progress_steps', []):
            step = step_data.copy()
            step['timestamp'] = datetime.fromisoformat(step['timestamp'])
            progress_steps.append(step)
        
        return cls(
            request=request,
            start_time=start_time,
            end_time=end_time,
            success=data.get('success', False),
            status=data.get('status', 'pending'),
            output_files=data.get('output_files', {}),
            error_message=data.get('error_message'),
            error_details=data.get('error_details', {}),
            progress_steps=progress_steps,
            current_step=data.get('current_step', 0),
            total_steps=data.get('total_steps', 6),
            statistics=data.get('statistics', {}),
            metadata=data.get('metadata', {})
        )
    
    def __str__(self) -> str:
        """String representation"""
        duration_str = f"{self.get_duration_seconds():.1f}s" if self.end_time else "ongoing"
        return (f"ReportResult(request={self.request.request_id}, "
                f"status={self.status}, "
                f"progress={self.get_progress_percentage():.1f}%, "
                f"duration={duration_str})")
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return self.__str__()