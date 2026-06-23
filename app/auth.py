"""
auth.py - JWT Authentication Utilities

Handles password hashing (bcrypt), JWT token creation,
and token verification for the authentication system.

Security Features:
    - Passwords are hashed using bcrypt (never stored in plaintext).
    - JWT tokens are signed with HS256 algorithm.
    - Tokens include an expiration timestamp.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Password Hashing Context
# Uses bcrypt as the primary hashing scheme.
# 'deprecated="auto"' allows automatic migration from older hash schemes.
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: The plaintext password to hash.

    Returns:
        The bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: The plaintext password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token.
              Must include "sub" (subject) with the username.
        expires_delta: Optional custom expiration time.
                       Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string to verify.

    Returns:
        The username (subject) from the token if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
