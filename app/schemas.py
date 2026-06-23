"""
schemas.py - Pydantic Validation Schemas

Defines request/response schemas for all API endpoints.
Pydantic models handle input validation, serialization,
and automatic documentation generation in Swagger UI.

Naming Convention:
    - *Create: Schema for creating a new record (request body).
    - *Update: Schema for updating an existing record (request body).
    - *Response: Schema for API responses (output).
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


# ==========================================================================
# USER SCHEMAS
# ==========================================================================

class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(
        ..., min_length=3, max_length=50,
        description="Unique username (3-50 characters)",
        examples=["john_doe"]
    )
    email: EmailStr = Field(
        ..., description="Valid email address",
        examples=["john@example.com"]
    )
    password: str = Field(
        ..., min_length=8, max_length=128,
        description="Password (minimum 8 characters)",
        examples=["StrongP@ss123"]
    )
    full_name: Optional[str] = Field(
        None, max_length=100,
        description="User's full name",
        examples=["John Doe"]
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username", examples=["john_doe"])
    password: str = Field(..., description="Password", examples=["StrongP@ss123"])


class UserResponse(BaseModel):
    """Schema for user information in API responses."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enables ORM mode (SQLAlchemy → Pydantic)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    username: Optional[str] = None


# ==========================================================================
# WORKOUT SCHEMAS
# ==========================================================================

class WorkoutCreate(BaseModel):
    """Schema for creating a new workout."""
    workout_name: str = Field(
        ..., min_length=1, max_length=100,
        description="Name of the workout",
        examples=["Morning Run"]
    )
    category: str = Field(
        ..., min_length=1, max_length=50,
        description="Workout category (e.g., Cardio, Strength, Flexibility, HIIT)",
        examples=["Cardio"]
    )
    duration_minutes: int = Field(
        ..., gt=0, le=1440,
        description="Duration in minutes (1-1440)",
        examples=[45]
    )
    calories_burned: Optional[float] = Field(
        None, ge=0,
        description="Estimated calories burned",
        examples=[350.0]
    )
    workout_date: date = Field(
        ..., description="Date of the workout (YYYY-MM-DD)",
        examples=["2026-06-13"]
    )
    notes: Optional[str] = Field(
        None, max_length=500,
        description="Additional notes about the workout",
        examples=["Felt great, increased pace in last 10 minutes"]
    )


class WorkoutUpdate(BaseModel):
    """Schema for updating an existing workout."""
    workout_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    duration_minutes: Optional[int] = Field(None, gt=0, le=1440)
    calories_burned: Optional[float] = Field(None, ge=0)
    workout_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class WorkoutResponse(BaseModel):
    """Schema for workout data in API responses."""
    id: int
    user_id: int
    workout_name: str
    category: str
    duration_minutes: int
    calories_burned: Optional[float] = None
    workout_date: date
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================================================
# GOAL SCHEMAS
# ==========================================================================

class GoalCreate(BaseModel):
    """Schema for creating a new fitness goal."""
    goal_name: str = Field(
        ..., min_length=1, max_length=100,
        description="Name of the goal",
        examples=["Run 100km this month"]
    )
    target_value: float = Field(
        ..., gt=0,
        description="Target value to achieve",
        examples=[100.0]
    )
    current_value: Optional[float] = Field(
        0.0, ge=0,
        description="Current progress value",
        examples=[25.0]
    )
    deadline: date = Field(
        ..., description="Goal deadline (YYYY-MM-DD)",
        examples=["2026-07-31"]
    )


class GoalUpdate(BaseModel):
    """Schema for updating an existing goal."""
    goal_name: Optional[str] = Field(None, min_length=1, max_length=100)
    target_value: Optional[float] = Field(None, gt=0)
    current_value: Optional[float] = Field(None, ge=0)
    deadline: Optional[date] = None
    is_achieved: Optional[bool] = None


class GoalResponse(BaseModel):
    """Schema for goal data in API responses."""
    id: int
    user_id: int
    goal_name: str
    target_value: float
    current_value: float
    deadline: date
    is_achieved: bool
    progress_percentage: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================================================
# WEIGHT LOG SCHEMAS
# ==========================================================================

class WeightLogCreate(BaseModel):
    """Schema for recording a new weight entry."""
    weight_kg: float = Field(
        ..., gt=0, le=700,
        description="Body weight in kilograms",
        examples=[75.5]
    )
    log_date: date = Field(
        ..., description="Date of measurement (YYYY-MM-DD)",
        examples=["2026-06-13"]
    )
    notes: Optional[str] = Field(
        None, max_length=300,
        description="Optional notes",
        examples=["Morning weight before breakfast"]
    )


class WeightLogUpdate(BaseModel):
    """Schema for updating a weight record."""
    weight_kg: Optional[float] = Field(None, gt=0, le=700)
    log_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=300)


class WeightLogResponse(BaseModel):
    """Schema for weight log data in API responses."""
    id: int
    user_id: int
    weight_kg: float
    log_date: date
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WeightProgressResponse(BaseModel):
    """Schema for weight progress statistics."""
    current_weight: Optional[float] = None
    starting_weight: Optional[float] = None
    lowest_weight: Optional[float] = None
    highest_weight: Optional[float] = None
    total_change: Optional[float] = None
    total_entries: int = 0
    entries: List[WeightLogResponse] = []


# ==========================================================================
# WATER LOG SCHEMAS
# ==========================================================================

class WaterLogCreate(BaseModel):
    """Schema for logging water intake."""
    amount_ml: float = Field(
        ..., gt=0, le=10000,
        description="Amount of water in milliliters",
        examples=[500.0]
    )
    log_date: date = Field(
        ..., description="Date of intake (YYYY-MM-DD)",
        examples=["2026-06-13"]
    )
    notes: Optional[str] = Field(
        None, max_length=300,
        description="Optional notes",
        examples=["After morning workout"]
    )


class WaterLogUpdate(BaseModel):
    """Schema for updating a water intake record."""
    amount_ml: Optional[float] = Field(None, gt=0, le=10000)
    log_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=300)


class WaterLogResponse(BaseModel):
    """Schema for water log data in API responses."""
    id: int
    user_id: int
    amount_ml: float
    log_date: date
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WaterDailySummary(BaseModel):
    """Schema for daily water intake summary."""
    log_date: date
    total_ml: float
    entry_count: int


class WaterWeeklySummary(BaseModel):
    """Schema for weekly water intake summary."""
    week_start: date
    week_end: date
    total_ml: float
    daily_average_ml: float
    entry_count: int


# ==========================================================================
# DASHBOARD SCHEMAS
# ==========================================================================

class DashboardResponse(BaseModel):
    """Schema for the main dashboard analytics."""
    total_workouts: int = 0
    total_calories_burned: float = 0.0
    total_workout_duration_minutes: int = 0
    active_goals: int = 0
    achieved_goals: int = 0
    goals_progress: List[GoalResponse] = []
    latest_weight: Optional[WeightLogResponse] = None
    weight_change_30_days: Optional[float] = None
    water_intake_today_ml: float = 0.0
    water_intake_7_day_avg_ml: float = 0.0
    recent_workouts: List[WorkoutResponse] = []
