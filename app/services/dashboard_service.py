"""
dashboard_service.py - Dashboard Analytics Service

Aggregates data from all models to provide a comprehensive
dashboard overview for the authenticated user.
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas


def get_dashboard_data(db: Session, user_id: int) -> schemas.DashboardResponse:
    """
    Compile dashboard analytics for a specific user.

    Aggregates:
        - Total workouts and calories burned
        - Goals progress (active + achieved)
        - Latest weight and 30-day weight change
        - Today's water intake and 7-day average
        - 5 most recent workouts

    Args:
        db: Database session.
        user_id: ID of the authenticated user.

    Returns:
        DashboardResponse with all aggregated statistics.
    """
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # --- Workout Statistics ---
    workout_stats = db.query(
        func.count(models.Workout.id).label("total_workouts"),
        func.coalesce(func.sum(models.Workout.calories_burned), 0).label("total_calories"),
        func.coalesce(func.sum(models.Workout.duration_minutes), 0).label("total_duration"),
    ).filter(models.Workout.user_id == user_id).first()

    # --- Goals ---
    active_goals_count = db.query(func.count(models.Goal.id)).filter(
        models.Goal.user_id == user_id,
        models.Goal.is_achieved == False,  # noqa: E712
    ).scalar()

    achieved_goals_count = db.query(func.count(models.Goal.id)).filter(
        models.Goal.user_id == user_id,
        models.Goal.is_achieved == True,  # noqa: E712
    ).scalar()

    # Get all goals with progress
    goals = db.query(models.Goal).filter(models.Goal.user_id == user_id).all()
    goals_progress = []
    for goal in goals:
        progress = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        goal_resp = schemas.GoalResponse(
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
        goals_progress.append(goal_resp)

    # --- Weight Statistics ---
    latest_weight = (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == user_id)
        .order_by(models.WeightLog.log_date.desc())
        .first()
    )

    weight_change = None
    if latest_weight:
        weight_30_days_ago = (
            db.query(models.WeightLog)
            .filter(
                models.WeightLog.user_id == user_id,
                models.WeightLog.log_date <= thirty_days_ago,
            )
            .order_by(models.WeightLog.log_date.desc())
            .first()
        )
        if weight_30_days_ago:
            weight_change = round(latest_weight.weight_kg - weight_30_days_ago.weight_kg, 2)

    # --- Water Intake Statistics ---
    water_today = db.query(
        func.coalesce(func.sum(models.WaterLog.amount_ml), 0)
    ).filter(
        models.WaterLog.user_id == user_id,
        models.WaterLog.log_date == today,
    ).scalar()

    water_7_day = db.query(
        func.coalesce(func.sum(models.WaterLog.amount_ml), 0)
    ).filter(
        models.WaterLog.user_id == user_id,
        models.WaterLog.log_date >= seven_days_ago,
    ).scalar()
    water_7_day_avg = round(water_7_day / 7, 2) if water_7_day else 0.0

    # --- Recent Workouts (last 5) ---
    recent_workouts = (
        db.query(models.Workout)
        .filter(models.Workout.user_id == user_id)
        .order_by(models.Workout.workout_date.desc())
        .limit(5)
        .all()
    )

    return schemas.DashboardResponse(
        total_workouts=workout_stats.total_workouts,
        total_calories_burned=float(workout_stats.total_calories),
        total_workout_duration_minutes=int(workout_stats.total_duration),
        active_goals=active_goals_count,
        achieved_goals=achieved_goals_count,
        goals_progress=goals_progress,
        latest_weight=latest_weight,
        weight_change_30_days=weight_change,
        water_intake_today_ml=float(water_today),
        water_intake_7_day_avg_ml=water_7_day_avg,
        recent_workouts=recent_workouts,
    )
