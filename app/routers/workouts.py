"""
routers/workouts.py - Workout Management Routes

Provides full CRUD operations for workout records.
All endpoints require JWT authentication.

Endpoints:
    POST   /api/v1/workouts/       - Create a new workout
    GET    /api/v1/workouts/       - Get all workouts for current user
    GET    /api/v1/workouts/{id}   - Get a specific workout by ID
    PUT    /api/v1/workouts/{id}   - Update a specific workout
    DELETE /api/v1/workouts/{id}   - Delete a specific workout
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/api/v1/workouts", tags=["Workouts"])


# ==========================================================================
# CREATE WORKOUT
# ==========================================================================

@router.post(
    "/",
    response_model=schemas.WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workout",
    description="Record a new workout session for the authenticated user.",
)
def create_workout(
    workout: schemas.WorkoutCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new workout record.

    The workout is automatically linked to the authenticated user.
    """
    new_workout = models.Workout(
        user_id=current_user.id,
        workout_name=workout.workout_name,
        category=workout.category,
        duration_minutes=workout.duration_minutes,
        calories_burned=workout.calories_burned,
        workout_date=workout.workout_date,
        notes=workout.notes,
    )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    return new_workout


# ==========================================================================
# GET ALL WORKOUTS
# ==========================================================================

@router.get(
    "/",
    response_model=List[schemas.WorkoutResponse],
    summary="Get all workouts",
    description="Retrieve all workouts for the authenticated user with optional filtering.",
)
def get_workouts(
    category: Optional[str] = Query(None, description="Filter by workout category"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all workouts for the authenticated user.

    Supports:
    - Category filtering (e.g., ?category=Cardio)
    - Pagination with skip and limit parameters
    - Results ordered by workout_date descending (newest first)
    """
    query = db.query(models.Workout).filter(
        models.Workout.user_id == current_user.id
    )

    # Apply category filter if provided
    if category:
        query = query.filter(models.Workout.category == category)

    workouts = (
        query.order_by(models.Workout.workout_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return workouts


# ==========================================================================
# GET SINGLE WORKOUT
# ==========================================================================

@router.get(
    "/{workout_id}",
    response_model=schemas.WorkoutResponse,
    summary="Get a specific workout",
    description="Retrieve a single workout by its ID.",
)
def get_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific workout by ID.

    Only returns workouts that belong to the authenticated user.
    """
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id,
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with ID {workout_id} not found",
        )

    return workout


# ==========================================================================
# UPDATE WORKOUT
# ==========================================================================

@router.put(
    "/{workout_id}",
    response_model=schemas.WorkoutResponse,
    summary="Update a workout",
    description="Update an existing workout. Only provided fields will be modified.",
)
def update_workout(
    workout_id: int,
    workout_update: schemas.WorkoutUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a specific workout.

    Only fields included in the request body will be updated.
    Null/missing fields remain unchanged.
    """
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id,
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with ID {workout_id} not found",
        )

    # Update only provided fields
    update_data = workout_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout, field, value)

    db.commit()
    db.refresh(workout)
    return workout


# ==========================================================================
# DELETE WORKOUT
# ==========================================================================

@router.delete(
    "/{workout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workout",
    description="Permanently delete a workout record.",
)
def delete_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific workout.

    Only the owner of the workout can delete it.
    Returns 204 No Content on success.
    """
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id,
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout with ID {workout_id} not found",
        )

    db.delete(workout)
    db.commit()
    return None
