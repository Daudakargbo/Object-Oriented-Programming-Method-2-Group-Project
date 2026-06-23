"""
routers/goals.py - Fitness Goals Management Routes

Provides CRUD operations and progress tracking for fitness goals.
All endpoints require JWT authentication.

Endpoints:
    POST   /api/v1/goals/              - Create a new goal
    GET    /api/v1/goals/              - Get all goals for current user
    GET    /api/v1/goals/{id}          - Get a specific goal by ID
    PUT    /api/v1/goals/{id}          - Update a specific goal
    DELETE /api/v1/goals/{id}          - Delete a specific goal
    PATCH  /api/v1/goals/{id}/progress - Update goal progress
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/api/v1/goals", tags=["Fitness Goals"])


# ==========================================================================
# CREATE GOAL
# ==========================================================================

@router.post(
    "/",
    response_model=schemas.GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fitness goal",
    description="Create a new fitness goal for the authenticated user.",
)
def create_goal(
    goal: schemas.GoalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new fitness goal.

    The goal is automatically linked to the authenticated user.
    Progress percentage is calculated as (current_value / target_value) * 100.
    """
    new_goal = models.Goal(
        user_id=current_user.id,
        goal_name=goal.goal_name,
        target_value=goal.target_value,
        current_value=goal.current_value if goal.current_value else 0.0,
        deadline=goal.deadline,
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    # Calculate progress percentage for response
    progress = (new_goal.current_value / new_goal.target_value * 100) if new_goal.target_value > 0 else 0
    return schemas.GoalResponse(
        id=new_goal.id,
        user_id=new_goal.user_id,
        goal_name=new_goal.goal_name,
        target_value=new_goal.target_value,
        current_value=new_goal.current_value,
        deadline=new_goal.deadline,
        is_achieved=new_goal.is_achieved,
        progress_percentage=round(progress, 2),
        created_at=new_goal.created_at,
        updated_at=new_goal.updated_at,
    )


# ==========================================================================
# GET ALL GOALS
# ==========================================================================

@router.get(
    "/",
    response_model=List[schemas.GoalResponse],
    summary="Get all fitness goals",
    description="Retrieve all fitness goals for the authenticated user.",
)
def get_goals(
    achieved: bool = Query(None, description="Filter by achievement status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all goals for the authenticated user.

    Supports:
    - Filter by achieved/active status
    - Pagination with skip and limit
    - Includes calculated progress_percentage
    """
    query = db.query(models.Goal).filter(models.Goal.user_id == current_user.id)

    if achieved is not None:
        query = query.filter(models.Goal.is_achieved == achieved)

    goals = query.order_by(models.Goal.deadline.asc()).offset(skip).limit(limit).all()

    # Map to response with progress percentage
    result = []
    for goal in goals:
        progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        result.append(schemas.GoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            goal_name=goal.goal_name,
            target_value=goal.target_value,
            current_value=goal.current_value,
            deadline=goal.deadline,
            is_achieved=goal.is_achieved,
            progress_percentage=round(progress, 2),
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        ))
    return result


# ==========================================================================
# GET SINGLE GOAL
# ==========================================================================

@router.get(
    "/{goal_id}",
    response_model=schemas.GoalResponse,
    summary="Get a specific goal",
    description="Retrieve a single fitness goal by its ID.",
)
def get_goal(
    goal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific goal by ID with calculated progress."""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )

    progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
    return schemas.GoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        goal_name=goal.goal_name,
        target_value=goal.target_value,
        current_value=goal.current_value,
        deadline=goal.deadline,
        is_achieved=goal.is_achieved,
        progress_percentage=round(progress, 2),
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


# ==========================================================================
# UPDATE GOAL
# ==========================================================================

@router.put(
    "/{goal_id}",
    response_model=schemas.GoalResponse,
    summary="Update a fitness goal",
    description="Update an existing fitness goal. Only provided fields will be modified.",
)
def update_goal(
    goal_id: int,
    goal_update: schemas.GoalUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a specific goal.

    Automatically checks if the goal should be marked as achieved
    when current_value >= target_value.
    """
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )

    # Update provided fields
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    # Auto-check if goal is achieved
    if goal.current_value >= goal.target_value:
        goal.is_achieved = True

    db.commit()
    db.refresh(goal)

    progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
    return schemas.GoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        goal_name=goal.goal_name,
        target_value=goal.target_value,
        current_value=goal.current_value,
        deadline=goal.deadline,
        is_achieved=goal.is_achieved,
        progress_percentage=round(min(progress, 100), 2),
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


# ==========================================================================
# UPDATE GOAL PROGRESS (PATCH - convenience endpoint)
# ==========================================================================

@router.patch(
    "/{goal_id}/progress",
    response_model=schemas.GoalResponse,
    summary="Update goal progress",
    description="Quick update to a goal's current progress value.",
)
def update_goal_progress(
    goal_id: int,
    current_value: float = Query(..., ge=0, description="New current progress value"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Quick-update a goal's progress.

    Convenience endpoint that only updates the current_value.
    Automatically marks the goal as achieved if current_value >= target_value.
    """
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )

    goal.current_value = current_value
    if current_value >= goal.target_value:
        goal.is_achieved = True

    db.commit()
    db.refresh(goal)

    progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
    return schemas.GoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        goal_name=goal.goal_name,
        target_value=goal.target_value,
        current_value=goal.current_value,
        deadline=goal.deadline,
        is_achieved=goal.is_achieved,
        progress_percentage=round(min(progress, 100), 2),
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


# ==========================================================================
# DELETE GOAL
# ==========================================================================

@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fitness goal",
    description="Permanently delete a fitness goal.",
)
def delete_goal(
    goal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific goal. Only the owner can delete it."""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id,
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found",
        )

    db.delete(goal)
    db.commit()
    return None
