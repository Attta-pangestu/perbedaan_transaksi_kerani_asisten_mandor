"""
Security Module for FFB Template System
"""

from .auth import hash_password, verify_password

__all__ = ['hash_password', 'verify_password']