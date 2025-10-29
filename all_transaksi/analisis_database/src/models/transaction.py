"""
Transaction Model
Represents FFB scanner transaction data with business logic methods
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class TransactionType(Enum):
    """Transaction record type based on RECORDTAG"""
    KERANI = "PM"      # Scanner/Data Entry
    MANDOR = "P1"      # Supervisor
    ASISTEN = "P5"     # Assistant


class TransactionStatus(Enum):
    """Transaction status codes"""
    NORMAL_731 = "731"
    NORMAL_732 = "732"
    SPECIAL_704 = "704"  # Special filter for May 2025


@dataclass
class Transaction:
    """
    Represents a single FFB scanner transaction
    """
    # Primary identifiers
    id: int
    transno: str
    scanuserid: str
    transdate: date
    transtime: datetime

    # Transaction metadata
    recordtag: TransactionType
    transstatus: TransactionStatus
    transtype: str

    # Location and organization
    fieldid: int
    ocid: int
    divid: Optional[int] = None
    divname: Optional[str] = None

    # Personnel
    workerid: Optional[int] = None
    carrierid: Optional[int] = None
    taskno: Optional[str] = None

    # Field measurements
    ripebch: float = 0.0
    unripebch: float = 0.0
    blackbch: float = 0.0
    rottenbch: float = 0.0
    longstalkbch: float = 0.0
    ratdmgbch: float = 0.0
    loosefruit: float = 0.0
    overripebch: float = 0.0
    underripebch: float = 0.0
    abnormalbch: float = 0.0
    loosefruit2: float = 0.0

    # System metadata
    uploaddatetime: Optional[datetime] = None
    lastuser: Optional[str] = None
    lastupdated: Optional[datetime] = None

    # Additional data from database row
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Transaction':
        """
        Create Transaction instance from database row

        :param row: Database row dictionary
        :return: Transaction instance
        """
        try:
            # Parse dates
            transdate = cls._parse_date(row.get('TRANSDATE'))
            transtime = cls._parse_time(row.get('TRANSTIME'))
            uploaddatetime = cls._parse_datetime(row.get('UPLOADDATETIME'))
            lastupdated = cls._parse_datetime(row.get('LASTUPDATED'))

            # Parse enums
            recordtag = TransactionType(row.get('RECORDTAG', 'PM'))
            transstatus = TransactionStatus(row.get('TRANSSTATUS', '731'))

            # Parse numeric values
            def safe_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default

            # Parse integer values
            def safe_int(value, default=0):
                try:
                    return int(value) if value else default
                except (ValueError, TypeError):
                    return default

            return cls(
                id=safe_int(row.get('ID')),
                transno=str(row.get('TRANSNO', '')).strip(),
                scanuserid=str(row.get('SCANUSERID', '')).strip(),
                transdate=transdate,
                transtime=transtime,
                recordtag=recordtag,
                transstatus=transstatus,
                transtype=str(row.get('TRANSTYPE', '')).strip(),
                fieldid=safe_int(row.get('FIELDID')),
                ocid=safe_int(row.get('OCID')),
                divid=safe_int(row.get('DIVID')) if row.get('DIVID') else None,
                divname=str(row.get('DIVNAME', '')).strip() or None,
                workerid=safe_int(row.get('WORKERID')) if row.get('WORKERID') else None,
                carrierid=safe_int(row.get('CARRIERID')) if row.get('CARRIERID') else None,
                taskno=str(row.get('TASKNO', '')).strip() or None,
                ripebch=safe_float(row.get('RIPEBCH')),
                unripebch=safe_float(row.get('UNRIPEBCH')),
                blackbch=safe_float(row.get('BLACKBCH')),
                rottenbch=safe_float(row.get('ROTTENBCH')),
                longstalkbch=safe_float(row.get('LONGSTALKBCH')),
                ratdmgbch=safe_float(row.get('RATDMGBCH')),
                loosefruit=safe_float(row.get('LOOSEFRUIT')),
                overripebch=safe_float(row.get('OVERRIPEBCH')),
                underripebch=safe_float(row.get('UNDERRIPEBCH')),
                abnormalbch=safe_float(row.get('ABNORMALBCH')),
                loosefruit2=safe_float(row.get('LOOSEFRUIT2')),
                uploaddatetime=uploaddatetime,
                lastuser=str(row.get('LASTUSER', '')).strip() or None,
                lastupdated=lastupdated,
                raw_data=row.copy()
            )
        except Exception as e:
            print(f"Error creating transaction from row: {e}")
            raise ValueError(f"Invalid transaction data: {e}")

    @staticmethod
    def _parse_date(date_value: Any) -> date:
        """Parse date value from various formats"""
        if date_value is None:
            return datetime.now().date()

        if isinstance(date_value, date):
            return date_value

        if isinstance(date_value, str):
            try:
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_value, fmt).date()
                    except ValueError:
                        continue
            except Exception:
                pass

        # Fallback to today
        return datetime.now().date()

    @staticmethod
    def _parse_time(time_value: Any) -> datetime:
        """Parse time value from various formats"""
        if time_value is None:
            return datetime.now()

        if isinstance(time_value, datetime):
            return time_value

        if isinstance(time_value, str):
            try:
                # Try different time formats
                for fmt in ['%H:%M:%S', '%H:%M', '%I:%M:%S %p']:
                    try:
                        time_obj = datetime.strptime(time_value, fmt).time()
                        return datetime.combine(datetime.now().date(), time_obj)
                    except ValueError:
                        continue
            except Exception:
                pass

        # Fallback to now
        return datetime.now()

    @staticmethod
    def _parse_datetime(datetime_value: Any) -> Optional[datetime]:
        """Parse datetime value from various formats"""
        if datetime_value is None:
            return None

        if isinstance(datetime_value, datetime):
            return datetime_value

        if isinstance(datetime_value, str):
            try:
                # Try different datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        return datetime.strptime(datetime_value, fmt)
                    except ValueError:
                        continue
            except Exception:
                pass

        return None

    def is_kerani(self) -> bool:
        """Check if this is a Kerani transaction"""
        return self.recordtag == TransactionType.KERANI

    def is_mandor(self) -> bool:
        """Check if this is a Mandor transaction"""
        return self.recordtag == TransactionType.MANDOR

    def is_asisten(self) -> bool:
        """Check if this is an Asisten transaction"""
        return self.recordtag == TransactionType.ASISTEN

    def is_verifier(self) -> bool:
        """Check if this is a verifier transaction (Mandor or Asisten)"""
        return self.recordtag in [TransactionType.MANDOR, TransactionType.ASISTEN]

    def has_special_status(self) -> bool:
        """Check if transaction has special status 704"""
        return self.transstatus == TransactionStatus.SPECIAL_704

    def get_field_data(self) -> Dict[str, float]:
        """
        Get all field measurement data as dictionary

        :return: Dictionary of field measurements
        """
        return {
            'ripebch': self.ripebch,
            'unripebch': self.unripebch,
            'blackbch': self.blackbch,
            'rottenbch': self.rottenbch,
            'longstalkbch': self.longstalkbch,
            'ratdmgbch': self.ratdmgbch,
            'loosefruit': self.loosefruit,
            'overripebch': self.overripebch,
            'underripebch': self.underripebch,
            'abnormalbch': self.abnormalbch,
            'loosefruit2': self.loosefruit2
        }

    def count_differences(self, other: 'Transaction') -> int:
        """
        Count field differences between this transaction and another

        :param other: Another transaction to compare with
        :return: Number of fields that differ
        """
        if not isinstance(other, Transaction):
            return 0

        fields_to_compare = [
            'ripebch', 'unripebch', 'blackbch', 'rottenbch',
            'longstalkbch', 'ratdmgbch', 'loosefruit'
        ]

        differences = 0
        for field in fields_to_compare:
            try:
                self_value = getattr(self, field)
                other_value = getattr(other, field)
                if self_value != other_value:
                    differences += 1
            except AttributeError:
                continue

        return differences

    def has_differences(self, other: 'Transaction') -> bool:
        """
        Check if this transaction has any field differences with another

        :param other: Another transaction to compare with
        :return: True if there are differences
        """
        return self.count_differences(other) > 0

    def can_verify_with(self, other: 'Transaction') -> bool:
        """
        Check if this transaction can verify another transaction

        :param other: Another transaction
        :return: True if transactions can verify each other
        """
        # Must have same TRANSNO
        if self.transno != other.transno:
            return False

        # Must have different record types
        if self.recordtag == other.recordtag:
            return False

        # One must be Kerani (PM) and other must be verifier (P1/P5)
        return (self.is_kerani() and other.is_verifier()) or \
               (self.is_verifier() and other.is_kerani())

    def get_verification_priority(self) -> int:
        """
        Get verification priority for this transaction type
        Higher number = higher priority

        :return: Priority value
        """
        if self.recordtag == TransactionType.ASISTEN:
            return 2  # Asisten has highest priority
        elif self.recordtag == TransactionType.MANDOR:
            return 1  # Mandor has medium priority
        else:
            return 0  # Kerani has lowest priority

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary representation

        :return: Dictionary representation
        """
        return {
            'id': self.id,
            'transno': self.transno,
            'scanuserid': self.scanuserid,
            'transdate': self.transdate.isoformat() if self.transdate else None,
            'transtime': self.transtime.isoformat() if self.transtime else None,
            'recordtag': self.recordtag.value if self.recordtag else None,
            'transstatus': self.transstatus.value if self.transstatus else None,
            'transtype': self.transtype,
            'fieldid': self.fieldid,
            'ocid': self.ocid,
            'divid': self.divid,
            'divname': self.divname,
            'workerid': self.workerid,
            'carrierid': self.carrierid,
            'taskno': self.taskno,
            'ripebch': self.ripebch,
            'unripebch': self.unripebch,
            'blackbch': self.blackbch,
            'rottenbch': self.rottenbch,
            'longstalkbch': self.longstalkbch,
            'ratdmgbch': self.ratdmgbch,
            'loosefruit': self.loosefruit,
            'overripebch': self.overripebch,
            'underripebch': self.underripebch,
            'abnormalbch': self.abnormalbch,
            'loosefruit2': self.loosefruit2,
            'uploaddatetime': self.uploaddatetime.isoformat() if self.uploaddatetime else None,
            'lastuser': self.lastuser,
            'lastupdated': self.lastupdated.isoformat() if self.lastupdated else None
        }

    def __str__(self) -> str:
        """String representation of transaction"""
        role_name = self.recordtag.name if self.recordtag else "UNKNOWN"
        return f"Transaction[{self.transno}] {role_name} by {self.scanuserid} on {self.transdate}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Transaction(id={self.id}, transno='{self.transno}', "
                f"scanuserid='{self.scanuserid}', recordtag={self.recordtag}, "
                f"transdate={self.transdate})")


class TransactionGroup:
    """
    Represents a group of transactions with the same TRANSNO
    Used for verification analysis
    """

    def __init__(self, transno: str):
        self.transno = transno
        self.transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction):
        """Add a transaction to this group"""
        if transaction.transno != self.transno:
            raise ValueError(f"Transaction TRANSNO mismatch: {transaction.transno} != {self.transno}")
        self.transactions.append(transaction)

    def get_kerani_transaction(self) -> Optional[Transaction]:
        """Get the Kerani transaction from this group"""
        for transaction in self.transactions:
            if transaction.is_kerani():
                return transaction
        return None

    def get_verifier_transactions(self) -> List[Transaction]:
        """Get all verifier transactions (Mandor/Asisten) from this group"""
        return [t for t in self.transactions if t.is_verifier()]

    def get_best_verifier(self, use_status_filter: bool = False) -> Optional[Transaction]:
        """
        Get the best verifier transaction based on priority

        :param use_status_filter: Apply status 704 filter
        :return: Best verifier transaction or None
        """
        verifiers = self.get_verifier_transactions()

        # Apply status filter if requested
        if use_status_filter:
            verifiers = [v for v in verifiers if v.has_special_status()]

        if not verifiers:
            return None

        # Sort by priority (Asisten > Mandor)
        verifiers.sort(key=lambda t: t.get_verification_priority(), reverse=True)
        return verifiers[0]

    def is_verified(self, use_status_filter: bool = False) -> bool:
        """
        Check if this transaction group is verified

        :param use_status_filter: Apply status 704 filter
        :return: True if verified
        """
        kerani = self.get_kerani_transaction()
        verifier = self.get_best_verifier(use_status_filter)

        return kerani is not None and verifier is not None

    def get_differences(self, use_status_filter: bool = False) -> int:
        """
        Get number of field differences between Kerani and best verifier

        :param use_status_filter: Apply status 704 filter
        :return: Number of differences
        """
        kerani = self.get_kerani_transaction()
        verifier = self.get_best_verifier(use_status_filter)

        if kerani and verifier:
            return kerani.count_differences(verifier)
        return 0

    def get_participants(self) -> List[str]:
        """Get list of participant user IDs"""
        return list(set(t.scanuserid for t in self.transactions))

    def get_roles(self) -> List[str]:
        """Get list of roles in this group"""
        return [t.recordtag.value for t in self.transactions]

    def size(self) -> int:
        """Get number of transactions in this group"""
        return len(self.transactions)

    def __str__(self) -> str:
        roles = ", ".join(self.get_roles())
        return f"TransactionGroup[{self.transno}] ({self.size()} transactions: {roles})"