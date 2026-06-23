"""
dependencies.py - Shared Dependencies for Route Handlers

Provides reusable dependency functions that are injected into
route handlers using FastAPI's Depends() mechanism.

Primary Dependency:
    - get_current_user: Extracts and validates the JWT token
      from the Authorization header and returns the authenticated user.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app import models

# ---------------------------------------------------------------------------
# OAuth2 Password Bearer Scheme
# Tells FastAPI to look for a Bearer token in the Authorization header.
# tokenUrl points to the login endpoint for Swagger UI integration.
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Dependency that authenticates the current user from the JWT token.

    This function:
    1. Extracts the Bearer token from the Authorization header.
    2. Verifies and decodes the JWT token.
    3. Looks up the user in the database.
    4. Returns the User object if everything is valid.

    Args:
        token: JWT token extracted from the Authorization header.
        db: Database session (injected by FastAPI).

    Returns:
        The authenticated User model instance.

    Raises:
        HTTPException 401: If the token is invalid or the user is not found.
        HTTPException 403: If the user account is inactive.
    """
    # Define the credentials exception for reuse
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the JWT token and extract the username
    username = verify_token(token)
    if username is None:
        raise credentials_exception

    # Look up the user in the database
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    # Check if the account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )

    return user
