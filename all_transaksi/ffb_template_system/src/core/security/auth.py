"""
Authentication and Authorization Utilities
"""

import bcrypt
from typing import Optional


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        # Convert to bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def generate_api_key() -> str:
    """
    Generate a random API key

    Returns:
        Random API key string
    """
    import secrets
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    return len(errors) == 0, errors