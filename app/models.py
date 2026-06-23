"""
models.py - SQLAlchemy ORM Models

Defines all database tables and their relationships for the
Fitness Tracker application.

Tables:
    - users: User accounts and profile information
    - workouts: Exercise/workout session records
    - goals: Fitness goals with progress tracking
    - weight_logs: Body weight tracking entries
    - water_logs: Daily water intake records

Relationships:
    - One User → Many Workouts
    - One User → Many Goals
    - One User → Many Weight Logs
    - One User → Many Water Logs
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    User model - stores account credentials and profile information.

    Attributes:
        id: Primary key.
        username: Unique username for login.
        email: Unique email address.
        hashed_password: Bcrypt-hashed password (never store plaintext!).
        full_name: User's display name.
        is_active: Whether the account is active.
        created_at: Timestamp of account creation.
        updated_at: Timestamp of last profile update.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships (one-to-many)
    workouts = relationship("Workout", back_populates="owner", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="owner", cascade="all, delete-orphan")
    weight_logs = relationship("WeightLog", back_populates="owner", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Workout(Base):
    """
    Workout model - records individual exercise sessions.

    Attributes:
        id: Primary key.
        user_id: Foreign key linking to the user.
        workout_name: Name/title of the workout.
        category: Type of workout (e.g., Cardio, Strength, Flexibility).
        duration_minutes: Duration of the workout in minutes.
        calories_burned: Estimated calories burned during the workout.
        workout_date: Date the workout was performed.
        notes: Optional additional notes about the workout.
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last update.
    """
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workout_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # e.g., Cardio, Strength, Flexibility, HIIT
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=True)
    workout_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship back to User
    owner = relationship("User", back_populates="workouts")

    def __repr__(self):
        return f"<Workout(id={self.id}, name='{self.workout_name}')>"


class Goal(Base):
    """
    Goal model - tracks fitness goals and their progress.

    Attributes:
        id: Primary key.
        user_id: Foreign key linking to the user.
        goal_name: Descriptive name for the goal.
        target_value: The target value to achieve.
        current_value: Current progress towards the goal.
        deadline: Target date for achieving the goal.
        is_achieved: Whether the goal has been completed.
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last update.
    """
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_name = Column(String(100), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    deadline = Column(Date, nullable=False)
    is_achieved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship back to User
    owner = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<Goal(id={self.id}, name='{self.goal_name}')>"


class WeightLog(Base):
    """
    WeightLog model - records body weight measurements over time.

    Attributes:
        id: Primary key.
        user_id: Foreign key linking to the user.
        weight_kg: Body weight in kilograms.
        log_date: Date of the weight measurement.
        notes: Optional notes (e.g., "morning weight", "after workout").
        created_at: Timestamp of record creation.
    """
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    log_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to User
    owner = relationship("User", back_populates="weight_logs")

    def __repr__(self):
        return f"<WeightLog(id={self.id}, weight={self.weight_kg}kg)>"


class WaterLog(Base):
    """
    WaterLog model - tracks daily water intake.

    Attributes:
        id: Primary key.
        user_id: Foreign key linking to the user.
        amount_ml: Amount of water consumed in milliliters.
        log_date: Date of the water intake record.
        notes: Optional notes (e.g., "morning", "during workout").
        created_at: Timestamp of record creation.
    """
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_ml = Column(Float, nullable=False)
    log_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to User
    owner = relationship("User", back_populates="water_logs")

    def __repr__(self):
        return f"<WaterLog(id={self.id}, amount={self.amount_ml}ml)>"
