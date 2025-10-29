"""
Report Request Model
Model for report generation requests
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from .report_template import ReportTemplate


@dataclass
class ReportRequest:
    """
    Model for report generation requests
    """
    
    # Required fields
    template: ReportTemplate
    selected_month: str  # Format: YYYY-MM
    selected_estates: List[str]
    
    # Export settings
    export_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Optional fields
    request_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    priority: str = "normal"  # low, normal, high
    
    # Additional parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.request_id is None:
            self.request_id = self._generate_request_id()
        
        # Ensure export_settings has required keys
        if 'formats' not in self.export_settings:
            self.export_settings['formats'] = ['PDF']
        
        if 'output_directory' not in self.export_settings:
            self.export_settings['output_directory'] = './reports'
        
        if 'filename_prefix' not in self.export_settings:
            self.export_settings['filename_prefix'] = 'report'
    
    def _generate_request_id(self) -> str:
        """
        Generate unique request ID
        
        Returns:
            Unique request ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"REQ_{timestamp}_{hash(str(self.selected_estates)) % 10000:04d}"
    
    def validate(self) -> bool:
        """
        Validate the report request
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Validate template
            if not self.template or not self.template.is_valid():
                return False
            
            # Validate month format
            if not self.selected_month:
                return False
            
            try:
                datetime.strptime(self.selected_month, "%Y-%m")
            except ValueError:
                return False
            
            # Validate estates
            if not self.selected_estates or len(self.selected_estates) == 0:
                return False
            
            # Validate export settings
            if not self.export_settings.get('formats'):
                return False
            
            # Validate supported formats
            supported_formats = ['PDF', 'Excel', 'CSV', 'JSON']
            for format_name in self.export_settings['formats']:
                if format_name not in supported_formats:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_validation_errors(self) -> List[str]:
        """
        Get detailed validation errors
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate template
        if not self.template:
            errors.append("Template is required")
        elif not self.template.is_valid():
            errors.append("Template is not valid")
        
        # Validate month
        if not self.selected_month:
            errors.append("Month selection is required")
        else:
            try:
                datetime.strptime(self.selected_month, "%Y-%m")
            except ValueError:
                errors.append("Invalid month format. Expected YYYY-MM")
        
        # Validate estates
        if not self.selected_estates:
            errors.append("Estate selection is required")
        elif len(self.selected_estates) == 0:
            errors.append("At least one estate must be selected")
        
        # Validate export settings
        if not self.export_settings.get('formats'):
            errors.append("Export format selection is required")
        else:
            supported_formats = ['PDF', 'Excel', 'CSV', 'JSON']
            for format_name in self.export_settings['formats']:
                if format_name not in supported_formats:
                    errors.append(f"Unsupported export format: {format_name}")
        
        return errors
    
    def is_valid(self) -> bool:
        """
        Check if request is valid
        
        Returns:
            True if valid, False otherwise
        """
        return len(self.get_validation_errors()) == 0
    
    def get_estimated_duration(self) -> int:
        """
        Get estimated generation duration in seconds
        
        Returns:
            Estimated duration in seconds
        """
        # Base duration
        base_duration = 30
        
        # Add time based on number of estates
        estate_factor = len(self.selected_estates) * 5
        
        # Add time based on export formats
        format_factor = len(self.export_settings.get('formats', [])) * 10
        
        # Priority adjustment
        priority_multiplier = {
            'low': 1.5,
            'normal': 1.0,
            'high': 0.8
        }.get(self.priority, 1.0)
        
        total_duration = int((base_duration + estate_factor + format_factor) * priority_multiplier)
        return max(total_duration, 10)  # Minimum 10 seconds
    
    def get_output_filenames(self) -> Dict[str, str]:
        """
        Get output filenames for each format
        
        Returns:
            Dictionary mapping format to filename
        """
        filenames = {}
        
        # Get settings
        output_dir = self.export_settings.get('output_directory', './reports')
        prefix = self.export_settings.get('filename_prefix', 'report')
        include_timestamp = self.export_settings.get('include_timestamp', True)
        
        # Generate timestamp suffix
        timestamp_suffix = ""
        if include_timestamp:
            timestamp_suffix = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate estate suffix
        estate_suffix = ""
        if len(self.selected_estates) == 1:
            estate_suffix = f"_{self.selected_estates[0]}"
        elif len(self.selected_estates) <= 3:
            estate_suffix = f"_{'_'.join(self.selected_estates)}"
        else:
            estate_suffix = f"_{len(self.selected_estates)}estates"
        
        # Generate month suffix
        month_suffix = f"_{self.selected_month.replace('-', '')}"
        
        # Generate filenames for each format
        for format_name in self.export_settings.get('formats', []):
            extension = {
                'PDF': '.pdf',
                'Excel': '.xlsx',
                'CSV': '.csv',
                'JSON': '.json'
            }.get(format_name, '.txt')
            
            filename = f"{prefix}{month_suffix}{estate_suffix}{timestamp_suffix}{extension}"
            full_path = f"{output_dir}/{filename}".replace('\\', '/')
            filenames[format_name] = full_path
        
        return filenames
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'request_id': self.request_id,
            'template': {
                'name': self.template.name,
                'template_id': self.template.template_id,
                'version': self.template.version
            },
            'selected_month': self.selected_month,
            'selected_estates': self.selected_estates,
            'export_settings': self.export_settings,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'priority': self.priority,
            'parameters': self.parameters,
            'estimated_duration': self.get_estimated_duration(),
            'output_filenames': self.get_output_filenames()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], template: ReportTemplate) -> 'ReportRequest':
        """
        Create from dictionary
        
        Args:
            data: Dictionary data
            template: Report template
            
        Returns:
            ReportRequest instance
        """
        # Parse created_at
        created_at = datetime.now()
        if 'created_at' in data:
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        return cls(
            template=template,
            selected_month=data['selected_month'],
            selected_estates=data['selected_estates'],
            export_settings=data.get('export_settings', {}),
            request_id=data.get('request_id'),
            created_at=created_at,
            created_by=data.get('created_by'),
            priority=data.get('priority', 'normal'),
            parameters=data.get('parameters', {})
        )
    
    def __str__(self) -> str:
        """String representation"""
        return (f"ReportRequest(id={self.request_id}, "
                f"template={self.template.name}, "
                f"month={self.selected_month}, "
                f"estates={len(self.selected_estates)}, "
                f"formats={self.export_settings.get('formats', [])})")
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return self.__str__()