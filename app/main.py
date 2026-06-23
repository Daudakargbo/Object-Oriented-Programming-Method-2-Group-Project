"""
main.py - FastAPI Application Entry Point

Initialises the FastAPI application, registers all routers,
and configures middleware, CORS, and startup events.

Run with:
    uvicorn app.main:app --reload

Swagger Documentation:
    http://localhost:8000/docs

ReDoc Documentation:
    http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine, ensure_database_exists
from app.routers import users, workouts, goals, weight, water

# Load application settings
settings = get_settings()

# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A production-ready REST API for tracking fitness activities, "
        "workouts, goals, body weight, and water intake. "
        "Built with FastAPI, PostgreSQL, and SQLAlchemy."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json",
    contact={
        "name": "Fitness Tracker Support",
        "email": "support@fitnesstracker.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# ---------------------------------------------------------------------------
# CORS Middleware
# Allows cross-origin requests from any frontend application.
# In production, restrict 'allow_origins' to your frontend domain.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup Event
# Creates all database tables if they don't exist.
# In production, use Alembic migrations instead.
# ---------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    """Create the database and tables on application startup."""
    ensure_database_exists(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Register Routers
# Each router handles a specific domain of the application.
# ---------------------------------------------------------------------------
app.include_router(users.router)
app.include_router(workouts.router)
app.include_router(goals.router)
app.include_router(weight.router)
app.include_router(water.router)


# ---------------------------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------------------------
@app.get(
    "/",
    tags=["Health Check"],
    summary="API Health Check",
    description="Returns basic information about the API status.",
)
def root():
    """
    Root endpoint - returns API status and links to documentation.
    """
    return {
        "message": f"Welcome to the {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Health Check",
    description="Simple health check endpoint for monitoring.",
)
def health_check():
    """Health check endpoint for load balancers and monitoring tools."""
    return {"status": "healthy"}
