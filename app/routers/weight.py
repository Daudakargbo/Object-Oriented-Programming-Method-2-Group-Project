"""
routers/weight.py - Weight Tracking Routes

Provides CRUD operations and progress statistics for body weight tracking.
All endpoints require JWT authentication.

Endpoints:
    POST   /api/v1/weight/           - Record a new weight entry
    GET    /api/v1/weight/           - Get weight history
    GET    /api/v1/weight/stats      - Get weight progress statistics
    GET    /api/v1/weight/{id}       - Get a specific weight record
    PUT    /api/v1/weight/{id}       - Update a weight record
    DELETE /api/v1/weight/{id}       - Delete a weight record
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/api/v1/weight", tags=["Weight Tracking"])


# ==========================================================================
# RECORD WEIGHT
# ==========================================================================

@router.post(
    "/",
    response_model=schemas.WeightLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new weight entry",
    description="Log a new body weight measurement.",
)
def record_weight(
    weight_log: schemas.WeightLogCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record a new body weight measurement.

    The entry is automatically linked to the authenticated user.
    """
    new_log = models.WeightLog(
        user_id=current_user.id,
        weight_kg=weight_log.weight_kg,
        log_date=weight_log.log_date,
        notes=weight_log.notes,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


# ==========================================================================
# GET WEIGHT HISTORY
# ==========================================================================

@router.get(
    "/",
    response_model=List[schemas.WeightLogResponse],
    summary="Get weight history",
    description="Retrieve all weight records for the authenticated user.",
)
def get_weight_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the weight history for the authenticated user.

    Results are ordered by log_date descending (newest first).
    """
    logs = (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == current_user.id)
        .order_by(models.WeightLog.log_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs


# ==========================================================================
# GET WEIGHT STATISTICS
# ==========================================================================

@router.get(
    "/stats",
    response_model=schemas.WeightProgressResponse,
    summary="Get weight progress statistics",
    description="Generate comprehensive weight progress statistics.",
)
def get_weight_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate weight progress statistics.

    Returns:
    - Current weight (most recent entry)
    - Starting weight (oldest entry)
    - Lowest and highest recorded weights
    - Total weight change (current - starting)
    - Total number of entries
    - Complete weight history
    """
    # Get all weight logs ordered by date
    all_logs = (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == current_user.id)
        .order_by(models.WeightLog.log_date.asc())
        .all()
    )

    if not all_logs:
        return schemas.WeightProgressResponse(total_entries=0)

    # Calculate statistics
    weights = [log.weight_kg for log in all_logs]
    starting_weight = weights[0]
    current_weight = weights[-1]
    lowest_weight = min(weights)
    highest_weight = max(weights)
    total_change = round(current_weight - starting_weight, 2)

    return schemas.WeightProgressResponse(
        current_weight=current_weight,
        starting_weight=starting_weight,
        lowest_weight=lowest_weight,
        highest_weight=highest_weight,
        total_change=total_change,
        total_entries=len(all_logs),
        entries=all_logs,
    )


# ==========================================================================
# GET SINGLE WEIGHT RECORD
# ==========================================================================

@router.get(
    "/{log_id}",
    response_model=schemas.WeightLogResponse,
    summary="Get a specific weight record",
    description="Retrieve a single weight record by its ID.",
)
def get_weight_log(
    log_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific weight log entry by ID."""
    log = db.query(models.WeightLog).filter(
        models.WeightLog.id == log_id,
        models.WeightLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weight log with ID {log_id} not found",
        )

    return log


# ==========================================================================
# UPDATE WEIGHT RECORD
# ==========================================================================

@router.put(
    "/{log_id}",
    response_model=schemas.WeightLogResponse,
    summary="Update a weight record",
    description="Update an existing weight record. Only provided fields will be modified.",
)
def update_weight_log(
    log_id: int,
    log_update: schemas.WeightLogUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a specific weight log entry."""
    log = db.query(models.WeightLog).filter(
        models.WeightLog.id == log_id,
        models.WeightLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weight log with ID {log_id} not found",
        )

    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)
    return log


# ==========================================================================
# DELETE WEIGHT RECORD
# ==========================================================================

@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a weight record",
    description="Permanently delete a weight record.",
)
def delete_weight_log(
    log_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific weight log entry."""
    log = db.query(models.WeightLog).filter(
        models.WeightLog.id == log_id,
        models.WeightLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weight log with ID {log_id} not found",
        )

    db.delete(log)
    db.commit()
    return None
