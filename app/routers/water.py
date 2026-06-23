"""
routers/water.py - Water Intake Tracking Routes

Provides CRUD operations and daily/weekly summaries for water intake.
All endpoints require JWT authentication.

Endpoints:
    POST   /api/v1/water/               - Log water intake
    GET    /api/v1/water/               - Get all water intake records
    GET    /api/v1/water/daily-summary  - Get daily water intake summaries
    GET    /api/v1/water/weekly-summary - Get weekly water intake summary
    GET    /api/v1/water/{id}           - Get a specific water record
    PUT    /api/v1/water/{id}           - Update a water record
    DELETE /api/v1/water/{id}           - Delete a water record
"""

from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/api/v1/water", tags=["Water Intake Tracking"])


# ==========================================================================
# LOG WATER INTAKE
# ==========================================================================

@router.post(
    "/",
    response_model=schemas.WaterLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log water intake",
    description="Record a new water intake entry.",
)
def log_water_intake(
    water_log: schemas.WaterLogCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log a new water intake record.

    Multiple entries can be logged per day to track individual
    drinks throughout the day.
    """
    new_log = models.WaterLog(
        user_id=current_user.id,
        amount_ml=water_log.amount_ml,
        log_date=water_log.log_date,
        notes=water_log.notes,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


# ==========================================================================
# GET ALL WATER RECORDS
# ==========================================================================

@router.get(
    "/",
    response_model=List[schemas.WaterLogResponse],
    summary="Get all water intake records",
    description="Retrieve all water intake records for the authenticated user.",
)
def get_water_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all water intake records.

    Results are ordered by log_date descending (newest first).
    """
    logs = (
        db.query(models.WaterLog)
        .filter(models.WaterLog.user_id == current_user.id)
        .order_by(models.WaterLog.log_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs


# ==========================================================================
# DAILY SUMMARY
# ==========================================================================

@router.get(
    "/daily-summary",
    response_model=List[schemas.WaterDailySummary],
    summary="Get daily water intake summaries",
    description="Get aggregated daily water intake for the past N days.",
)
def get_daily_summary(
    days: int = Query(7, ge=1, le=365, description="Number of past days to include"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get daily water intake summaries.

    Aggregates all water intake entries per day for the specified
    number of past days. Returns total_ml and entry_count per day.
    """
    start_date = date.today() - timedelta(days=days - 1)

    daily_data = (
        db.query(
            models.WaterLog.log_date,
            func.sum(models.WaterLog.amount_ml).label("total_ml"),
            func.count(models.WaterLog.id).label("entry_count"),
        )
        .filter(
            models.WaterLog.user_id == current_user.id,
            models.WaterLog.log_date >= start_date,
        )
        .group_by(models.WaterLog.log_date)
        .order_by(models.WaterLog.log_date.desc())
        .all()
    )

    return [
        schemas.WaterDailySummary(
            log_date=row.log_date,
            total_ml=float(row.total_ml),
            entry_count=row.entry_count,
        )
        for row in daily_data
    ]


# ==========================================================================
# WEEKLY SUMMARY
# ==========================================================================

@router.get(
    "/weekly-summary",
    response_model=schemas.WaterWeeklySummary,
    summary="Get weekly water intake summary",
    description="Get aggregated water intake for the past 7 days.",
)
def get_weekly_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a weekly water intake summary.

    Returns the total water consumed, daily average,
    and number of entries for the past 7 days.
    """
    today = date.today()
    week_start = today - timedelta(days=6)

    # Query total water intake for the past week
    result = db.query(
        func.coalesce(func.sum(models.WaterLog.amount_ml), 0).label("total_ml"),
        func.count(models.WaterLog.id).label("entry_count"),
    ).filter(
        models.WaterLog.user_id == current_user.id,
        models.WaterLog.log_date >= week_start,
        models.WaterLog.log_date <= today,
    ).first()

    total_ml = float(result.total_ml)
    daily_average = round(total_ml / 7, 2)

    return schemas.WaterWeeklySummary(
        week_start=week_start,
        week_end=today,
        total_ml=total_ml,
        daily_average_ml=daily_average,
        entry_count=result.entry_count,
    )


# ==========================================================================
# GET SINGLE WATER RECORD
# ==========================================================================

@router.get(
    "/{log_id}",
    response_model=schemas.WaterLogResponse,
    summary="Get a specific water intake record",
    description="Retrieve a single water intake record by its ID.",
)
def get_water_log(
    log_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific water log entry by ID."""
    log = db.query(models.WaterLog).filter(
        models.WaterLog.id == log_id,
        models.WaterLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water log with ID {log_id} not found",
        )

    return log


# ==========================================================================
# UPDATE WATER RECORD
# ==========================================================================

@router.put(
    "/{log_id}",
    response_model=schemas.WaterLogResponse,
    summary="Update a water intake record",
    description="Update an existing water intake record.",
)
def update_water_log(
    log_id: int,
    log_update: schemas.WaterLogUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a specific water log entry."""
    log = db.query(models.WaterLog).filter(
        models.WaterLog.id == log_id,
        models.WaterLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water log with ID {log_id} not found",
        )

    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)
    return log


# ==========================================================================
# DELETE WATER RECORD
# ==========================================================================

@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a water intake record",
    description="Permanently delete a water intake record.",
)
def delete_water_log(
    log_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific water log entry."""
    log = db.query(models.WaterLog).filter(
        models.WaterLog.id == log_id,
        models.WaterLog.user_id == current_user.id,
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water log with ID {log_id} not found",
        )

    db.delete(log)
    db.commit()
    return None
