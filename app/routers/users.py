"""
routers/users.py - User Authentication & Profile Routes

Endpoints:
    POST   /api/v1/users/register  - Register a new user
    POST   /api/v1/users/login     - Login and get JWT token
    GET    /api/v1/users/me         - Get current user profile
    PUT    /api/v1/users/me         - Update current user profile
    GET    /api/v1/users/dashboard  - Get dashboard analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from app import models, schemas
from app.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/api/v1/users", tags=["Users & Authentication"])


# ==========================================================================
# REGISTRATION
# ==========================================================================

@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Username and email must be unique.",
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Steps:
    1. Check if username already exists.
    2. Check if email already exists.
    3. Hash the password using bcrypt.
    4. Create the user record in the database.
    5. Return the created user (without password).
    """
    # Check for existing username
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check for existing email
    existing_email = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user with hashed password
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==========================================================================
# LOGIN
# ==========================================================================

@router.post(
    "/login",
    response_model=schemas.Token,
    summary="Login and get JWT token",
    description="Authenticate with username and password to receive a JWT access token.",
)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.

    Steps:
    1. Find the user by username.
    2. Verify the password against the stored hash.
    3. Generate and return a JWT access token.
    """
    # Find user by username
    user = db.query(models.User).filter(
        models.User.username == user_credentials.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Create JWT access token
    access_token = create_access_token(data={"sub": user.username})

    return schemas.Token(access_token=access_token, token_type="bearer")


# ==========================================================================
# PROFILE
# ==========================================================================

@router.get(
    "/me",
    response_model=schemas.UserResponse,
    summary="Get current user profile",
    description="Retrieve the profile of the currently authenticated user.",
)
def get_profile(current_user: models.User = Depends(get_current_user)):
    """Return the authenticated user's profile information."""
    return current_user


@router.put(
    "/me",
    response_model=schemas.UserResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user.",
)
def update_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated user's profile.

    Only the fields provided in the request body will be updated.
    """
    # Update only the fields that were provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    if user_update.email is not None:
        # Check if the new email is already taken by another user
        existing_email = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id,
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user",
            )
        current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)
    return current_user


# ==========================================================================
# DASHBOARD
# ==========================================================================

@router.get(
    "/dashboard",
    response_model=schemas.DashboardResponse,
    summary="Get dashboard analytics",
    description="Retrieve comprehensive fitness dashboard with all statistics.",
)
def get_dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the dashboard analytics for the authenticated user.

    Includes:
    - Total workouts and calories burned
    - Goals progress
    - Weight progress
    - Water intake statistics
    - Recent workouts
    """
    return get_dashboard_data(db=db, user_id=current_user.id)
