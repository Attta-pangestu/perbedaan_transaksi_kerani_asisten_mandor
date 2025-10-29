"""
Estate Model
Represents estate data with divisions and database configuration
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .division import Division, DivisionManager


@dataclass
class Estate:
    """
    Represents an estate in the FFB system
    """
    name: str
    database_path: str
    id: Optional[str] = None

    # Division management
    division_manager: DivisionManager = field(default_factory=DivisionManager)

    # Connection settings
    username: str = 'sysdba'
    password: str = 'masterkey'
    use_localhost: bool = False

    # Estate status
    is_connected: bool = False
    last_tested: Optional[str] = None
    connection_error: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing"""
        if self.id is None:
            # Generate ID from name
            self.id = self.name.upper().replace(' ', '_').replace('-', '_')

    @classmethod
    def from_config(cls, name: str, database_path: str, **kwargs) -> 'Estate':
        """
        Create Estate instance from configuration

        :param name: Estate name
        :param database_path: Database file path
        :param kwargs: Additional configuration options
        :return: Estate instance
        """
        return cls(
            name=name,
            database_path=database_path,
            id=kwargs.get('id'),
            username=kwargs.get('username', 'sysdba'),
            password=kwargs.get('password', 'masterkey'),
            use_localhost=kwargs.get('use_localhost', False)
        )

    def add_division(self, division: Division):
        """
        Add a division to this estate

        :param division: Division to add
        """
        # Set estate context for division
        division.estate = self.name
        self.division_manager.add_division(division)

    def get_division(self, div_id: str) -> Optional[Division]:
        """
        Get division by ID

        :param div_id: Division ID
        :return: Division or None
        """
        return self.division_manager.get_division(div_id)

    def get_or_create_division(self, div_id: str, div_name: Optional[str] = None) -> Division:
        """
        Get existing division or create new one

        :param div_id: Division ID
        :param div_name: Division name (optional)
        :return: Division instance
        """
        division = self.division_manager.get_or_create_division(div_id, div_name)
        # Set estate context
        division.estate = self.name
        return division

    def get_active_divisions(self) -> List[Division]:
        """
        Get all divisions with transaction data

        :return: List of active divisions
        """
        return self.division_manager.get_active_divisions()

    def has_data(self) -> bool:
        """
        Check if this estate has any transaction data

        :return: True if estate has data
        """
        return len(self.get_active_divisions()) > 0

    def get_summary_dict(self) -> Dict[str, Any]:
        """
        Get summary statistics for this estate

        :return: Dictionary with summary statistics
        """
        division_totals = self.division_manager.get_totals()

        return {
            'estate_id': self.id,
            'estate_name': self.name,
            'database_path': self.database_path,
            'is_connected': self.is_connected,
            'last_tested': self.last_tested,
            'connection_error': self.connection_error,
            'division_count': self.division_manager.get_division_count(),
            'active_division_count': self.division_manager.get_active_division_count(),
            'total_transactions': division_totals['kerani'],
            'kerani_transactions': division_totals['kerani'],
            'mandor_transactions': division_totals['mandor'],
            'asisten_transactions': division_totals['asisten'],
            'verified_transactions': division_totals['verified'],
            'differences_count': division_totals['differences'],
            'verification_rate': division_totals['verification_rate'],
            'difference_rate': division_totals['difference_rate'],
            'has_data': self.has_data()
        }

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information for this estate

        :return: Dictionary with connection info
        """
        return {
            'name': self.name,
            'database_path': self.database_path,
            'username': self.username,
            'password': self.password,
            'use_localhost': self.use_localhost,
            'is_connected': self.is_connected,
            'connection_error': self.connection_error
        }

    def mark_connection_success(self):
        """Mark estate connection as successful"""
        self.is_connected = True
        self.connection_error = None
        from datetime import datetime
        self.last_tested = datetime.now().isoformat()

    def mark_connection_failure(self, error_message: str):
        """Mark estate connection as failed"""
        self.is_connected = False
        self.connection_error = error_message
        from datetime import datetime
        self.last_tested = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert estate to dictionary representation

        :return: Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'database_path': self.database_path,
            'connection_info': self.get_connection_info(),
            'summary': self.get_summary_dict(),
            'divisions': [div.to_dict() for div in self.get_active_divisions()]
        }

    def __str__(self) -> str:
        """String representation"""
        status = "✓" if self.is_connected else "✗"
        return f"Estate[{self.name}] {status} ({self.division_manager.get_active_division_count()} active divisions)"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Estate(id='{self.id}', name='{self.name}', "
                f"database_path='{self.database_path}', "
                f"connected={self.is_connected}, "
                f"divisions={self.division_manager.get_active_division_count()})")


class EstateManager:
    """
    Manages collection of estates with configuration and aggregation capabilities
    """

    def __init__(self):
        self.estates: Dict[str, Estate] = {}

    def add_estate(self, estate: Estate):
        """
        Add or update an estate

        :param estate: Estate to add
        """
        self.estates[estate.id] = estate

    def get_estate(self, estate_id: str) -> Optional[Estate]:
        """
        Get estate by ID

        :param estate_id: Estate ID
        :return: Estate or None
        """
        return self.estates.get(estate_id)

    def get_estate_by_name(self, name: str) -> Optional[Estate]:
        """
        Get estate by name

        :param name: Estate name
        :return: Estate or None
        """
        for estate in self.estates.values():
            if estate.name == name:
                return estate
        return None

    def get_or_create_estate(self, name: str, database_path: str, **kwargs) -> Estate:
        """
        Get existing estate or create new one

        :param name: Estate name
        :param database_path: Database file path
        :param kwargs: Additional configuration options
        :return: Estate instance
        """
        # Generate ID from name
        estate_id = name.upper().replace(' ', '_').replace('-', '_')

        if estate_id in self.estates:
            return self.estates[estate_id]
        else:
            estate = Estate.from_config(name, database_path, **kwargs)
            self.estates[estate_id] = estate
            return estate

    def get_active_estates(self) -> List[Estate]:
        """
        Get all estates with transaction data

        :return: List of active estates
        """
        return [estate for estate in self.estates.values() if estate.has_data()]

    def get_connected_estates(self) -> List[Estate]:
        """
        Get all estates with successful database connections

        :return: List of connected estates
        """
        return [estate for estate in self.estates.values() if estate.is_connected]

    def get_estate_count(self) -> int:
        """Get total estate count"""
        return len(self.estates)

    def get_active_estate_count(self) -> int:
        """Get active estate count"""
        return len(self.get_active_estates())

    def get_connected_estate_count(self) -> int:
        """Get connected estate count"""
        return len(self.get_connected_estates())

    def get_totals(self) -> Dict[str, Any]:
        """
        Get total transaction counts across all estates

        :return: Dictionary with total counts
        """
        totals = {
            'estates': self.get_estate_count(),
            'active_estates': self.get_active_estate_count(),
            'connected_estates': self.get_connected_estate_count(),
            'kerani': 0,
            'mandor': 0,
            'asisten': 0,
            'verified': 0,
            'differences': 0
        }

        # Aggregate totals from all estates
        for estate in self.estates.values():
            estate_totals = estate.division_manager.get_totals()
            totals['kerani'] += estate_totals['kerani']
            totals['mandor'] += estate_totals['mandor']
            totals['asisten'] += estate_totals['asisten']
            totals['verified'] += estate_totals['verified']
            totals['differences'] += estate_totals['differences']

        # Calculate overall verification rate
        if totals['kerani'] > 0:
            totals['verification_rate'] = (totals['verified'] / totals['kerani']) * 100
        else:
            totals['verification_rate'] = 0.0

        # Calculate overall difference rate
        if totals['verified'] > 0:
            totals['difference_rate'] = (totals['differences'] / totals['verified']) * 100
        else:
            totals['difference_rate'] = 0.0

        return totals

    def get_all_divisions(self) -> List[Division]:
        """
        Get all divisions from all estates

        :return: List of all divisions
        """
        all_divisions = []
        for estate in self.estates.values():
            all_divisions.extend(estate.division_manager.divisions.values())
        return all_divisions

    def get_connection_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of connection status across all estates

        :return: Dictionary with connection status
        """
        connected = self.get_connected_estates()
        active = self.get_active_estates()
        total = self.get_estate_count()

        return {
            'total_estates': total,
            'connected_estates': len(connected),
            'active_estates': len(active),
            'connection_rate': (len(connected) / total * 100) if total > 0 else 0,
            'active_rate': (len(active) / total * 100) if total > 0 else 0,
            'connected_estate_names': [estate.name for estate in connected],
            'disconnected_estates': [
                {
                    'name': estate.name,
                    'error': estate.connection_error
                }
                for estate in self.estates.values()
                if not estate.is_connected
            ]
        }

    def clear(self):
        """Clear all estates"""
        self.estates.clear()

    def __len__(self) -> int:
        """Get number of estates"""
        return len(self.estates)

    def __iter__(self):
        """Iterate over estates"""
        return iter(self.estates.values())

    def __str__(self) -> str:
        """String representation"""
        active = self.get_active_estate_count()
        connected = self.get_connected_estate_count()
        total = self.get_estate_count()
        return f"EstateManager({total} estates, {connected} connected, {active} active)"