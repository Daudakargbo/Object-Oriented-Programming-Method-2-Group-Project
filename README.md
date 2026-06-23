# 🏋️ Fitness Tracker API

A **production-ready REST API** for tracking fitness activities, workouts, goals, body weight, and water intake. Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **JWT Authentication**.


---

##  Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [API Endpoints](#-api-endpoints)
- [Example API Requests & Responses](#-example-api-requests--responses)
- [Postman Testing Guide](#-postman-testing-guide)
- [Environment Variables](#-environment-variables)
- [Database Schema](#-database-schema)
- [License](#-license)

---

##  Features

| Feature | Description |
|---------|-------------|
|  **User Authentication** | Registration, login, JWT tokens, bcrypt password hashing |
| 🏃 **Workout Management** | Full CRUD with category filtering and pagination |
| 🎯 **Fitness Goals** | Goal tracking with auto-achievement detection |
| ⚖️ **Weight Tracking** | Body weight logging with progress statistics |
| 💧 **Water Intake** | Daily/weekly summaries and intake tracking |
| 📊 **Dashboard Analytics** | Comprehensive fitness overview with aggregated stats |
| 📝 **Swagger Docs** | Interactive API documentation at `/docs` |
| 🔄 **Alembic Migrations** | Database version control and schema management |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework (async, type-safe) |
| **PostgreSQL** | Relational database |
| **SQLAlchemy** | ORM (Object-Relational Mapping) |
| **Alembic** | Database migrations |
| **Pydantic** | Data validation & serialization |
| **python-jose** | JWT token encoding/decoding |
| **passlib + bcrypt** | Password hashing |
| **Uvicorn** | ASGI server |

---

## 📁 Project Structure

```
fitness_tracker/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py           # Database connection & session management
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic validation schemas
│   ├── auth.py               # JWT & password hashing utilities
│   ├── dependencies.py       # Shared dependencies (auth middleware)
│   ├── config.py             # Application configuration (env vars)
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py          # User auth & profile routes
│   │   ├── workouts.py       # Workout CRUD routes
│   │   ├── goals.py          # Goals CRUD & progress routes
│   │   ├── weight.py         # Weight tracking routes
│   │   └── water.py          # Water intake tracking routes
│   │
│   └── services/
│       ├── __init__.py
│       └── dashboard_service.py  # Dashboard analytics logic
│
├── alembic/
│   ├── env.py                # Alembic environment configuration
│   ├── script.py.mako        # Migration script template
│   └── versions/             # Migration scripts
│
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # This file
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 14+** — [Download PostgreSQL](https://www.postgresql.org/download/)
- **pip** — Python package manager (included with Python)
- **Git** — Version control (optional)

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fitness_tracker
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the `.env` file and update the values:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/fitness_tracker

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_NAME=Fitness Tracker API
APP_VERSION=1.0.0
DEBUG=True
```

> ⚠️ **Important**: Change `SECRET_KEY` to a strong random string in production!

---

## 🗄️ Database Setup

### 1. Create the PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create the database
CREATE DATABASE fitness_tracker;

-- Verify creation
\l

-- Exit
\q
```

### 2. Run Alembic Migrations

```bash
# Generate the initial migration
alembic revision --autogenerate -m "Initial migration - create all tables"

# Apply the migration
alembic upgrade head
```

### Alternative: Auto-create Tables

The application also creates tables automatically on startup (via `Base.metadata.create_all()`). Simply start the app and tables will be created if they don't exist.

---

## ▶ Running the Application

### Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

### With Custom Host/Port

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📖 API Documentation

Once the server is running, access the interactive documentation:

| Documentation | URL |
|---------------|-----|
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| **OpenAPI JSON** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) |

---

## 📡 API Endpoints

### 🔐 Users & Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/users/register` | Register a new user | ❌ |
| `POST` | `/api/v1/users/login` | Login & get JWT token | ❌ |
| `GET` | `/api/v1/users/me` | Get current user profile | ✅ |
| `PUT` | `/api/v1/users/me` | Update current user profile | ✅ |
| `GET` | `/api/v1/users/dashboard` | Get dashboard analytics | ✅ |

### 🏃 Workouts

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/workouts/` | Create a new workout | ✅ |
| `GET` | `/api/v1/workouts/` | Get all workouts | ✅ |
| `GET` | `/api/v1/workouts/{id}` | Get a specific workout | ✅ |
| `PUT` | `/api/v1/workouts/{id}` | Update a workout | ✅ |
| `DELETE` | `/api/v1/workouts/{id}` | Delete a workout | ✅ |

### 🎯 Fitness Goals

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/goals/` | Create a new goal | ✅ |
| `GET` | `/api/v1/goals/` | Get all goals | ✅ |
| `GET` | `/api/v1/goals/{id}` | Get a specific goal | ✅ |
| `PUT` | `/api/v1/goals/{id}` | Update a goal | ✅ |
| `PATCH` | `/api/v1/goals/{id}/progress` | Update goal progress | ✅ |
| `DELETE` | `/api/v1/goals/{id}` | Delete a goal | ✅ |

### ⚖️ Weight Tracking

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/weight/` | Record a new weight entry | ✅ |
| `GET` | `/api/v1/weight/` | Get weight history | ✅ |
| `GET` | `/api/v1/weight/stats` | Get weight statistics | ✅ |
| `GET` | `/api/v1/weight/{id}` | Get a specific weight record | ✅ |
| `PUT` | `/api/v1/weight/{id}` | Update a weight record | ✅ |
| `DELETE` | `/api/v1/weight/{id}` | Delete a weight record | ✅ |

### 💧 Water Intake

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/water/` | Log water intake | ✅ |
| `GET` | `/api/v1/water/` | Get all water records | ✅ |
| `GET` | `/api/v1/water/daily-summary` | Daily water summaries | ✅ |
| `GET` | `/api/v1/water/weekly-summary` | Weekly water summary | ✅ |
| `GET` | `/api/v1/water/{id}` | Get a specific water record | ✅ |
| `PUT` | `/api/v1/water/{id}` | Update a water record | ✅ |
| `DELETE` | `/api/v1/water/{id}` | Delete a water record | ✅ |

### ❤️ Health Check

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | API info & status | ❌ |
| `GET` | `/health` | Health check | ❌ |

---

## 📝 Example API Requests & Responses

### 1. Register a New User

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "StrongP@ss123",
    "full_name": "John Doe"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-06-13T14:00:00.000000+00:00",
  "updated_at": "2026-06-13T14:00:00.000000+00:00"
}
```

### 2. Login

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "StrongP@ss123"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create a Workout (Authenticated)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/workouts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "workout_name": "Morning Run",
    "category": "Cardio",
    "duration_minutes": 45,
    "calories_burned": 350.0,
    "workout_date": "2026-06-13",
    "notes": "Felt great, increased pace in last 10 minutes"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "workout_name": "Morning Run",
  "category": "Cardio",
  "duration_minutes": 45,
  "calories_burned": 350.0,
  "workout_date": "2026-06-13",
  "notes": "Felt great, increased pace in last 10 minutes",
  "created_at": "2026-06-13T14:05:00.000000+00:00",
  "updated_at": "2026-06-13T14:05:00.000000+00:00"
}
```

### 4. Create a Fitness Goal

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/goals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "goal_name": "Run 100km this month",
    "target_value": 100.0,
    "current_value": 25.0,
    "deadline": "2026-07-31"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "goal_name": "Run 100km this month",
  "target_value": 100.0,
  "current_value": 25.0,
  "deadline": "2026-07-31",
  "is_achieved": false,
  "progress_percentage": 25.0,
  "created_at": "2026-06-13T14:10:00.000000+00:00",
  "updated_at": null
}
```

### 5. Record Body Weight

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/weight/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "weight_kg": 75.5,
    "log_date": "2026-06-13",
    "notes": "Morning weight before breakfast"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "weight_kg": 75.5,
  "log_date": "2026-06-13",
  "notes": "Morning weight before breakfast",
  "created_at": "2026-06-13T14:15:00.000000+00:00"
}
```

### 6. Log Water Intake

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/water/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "amount_ml": 500.0,
    "log_date": "2026-06-13",
    "notes": "After morning workout"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "amount_ml": 500.0,
  "log_date": "2026-06-13",
  "notes": "After morning workout",
  "created_at": "2026-06-13T14:20:00.000000+00:00"
}
```

### 7. Get Dashboard Analytics

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/users/dashboard \
  -H "Authorization: Bearer <your_token>"
```

**Response (200 OK):**
```json
{
  "total_workouts": 5,
  "total_calories_burned": 1750.0,
  "total_workout_duration_minutes": 225,
  "active_goals": 2,
  "achieved_goals": 1,
  "goals_progress": [
    {
      "id": 1,
      "goal_name": "Run 100km this month",
      "target_value": 100.0,
      "current_value": 25.0,
      "progress_percentage": 25.0,
      "is_achieved": false,
      "deadline": "2026-07-31"
    }
  ],
  "latest_weight": {
    "weight_kg": 74.2,
    "log_date": "2026-06-13"
  },
  "weight_change_30_days": -1.3,
  "water_intake_today_ml": 2500.0,
  "water_intake_7_day_avg_ml": 2200.0,
  "recent_workouts": []
}
```

### 8. Error Response Example

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Workout with ID 99 not found"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Username already registered"
}
```

**Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    }
  ]
}
```

---

## 🧪 Postman Testing Guide

### Setting Up Postman

1. **Import the API** — Use the OpenAPI spec URL:
   ```
   http://localhost:8000/openapi.json
   ```
   Go to Postman → Import → Link → Paste the URL

2. **Create an Environment** with these variables:

   | Variable | Initial Value |
   |----------|---------------|
   | `base_url` | `http://localhost:8000` |
   | `token` | *(leave empty, will be set after login)* |

3. **Set Authorization** — For all authenticated requests:
   - Type: `Bearer Token`
   - Token: `{{token}}`

### Testing Workflow

#### Step 1: Register a User
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/users/register`
- **Body (JSON):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "TestPass123!",
  "full_name": "Test User"
}
```

#### Step 2: Login & Save Token
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/users/login`
- **Body (JSON):**
```json
{
  "username": "testuser",
  "password": "TestPass123!"
}
```
- **Tests Tab** (Auto-save token):
```javascript
// Auto-save the token to environment variable
var response = pm.response.json();
pm.environment.set("token", response.access_token);
console.log("Token saved:", response.access_token);
```

#### Step 3: Create a Workout
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/workouts/`
- **Headers:** `Authorization: Bearer {{token}}`
- **Body (JSON):**
```json
{
  "workout_name": "Evening Gym Session",
  "category": "Strength",
  "duration_minutes": 60,
  "calories_burned": 400.0,
  "workout_date": "2026-06-13",
  "notes": "Leg day - squats, lunges, leg press"
}
```

#### Step 4: Create a Goal
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/goals/`
- **Headers:** `Authorization: Bearer {{token}}`
- **Body (JSON):**
```json
{
  "goal_name": "Lose 5kg by August",
  "target_value": 5.0,
  "current_value": 1.2,
  "deadline": "2026-08-31"
}
```

#### Step 5: Log Weight
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/weight/`
- **Headers:** `Authorization: Bearer {{token}}`
- **Body (JSON):**
```json
{
  "weight_kg": 78.3,
  "log_date": "2026-06-13",
  "notes": "Morning weight"
}
```

#### Step 6: Log Water
- **Method:** `POST`
- **URL:** `{{base_url}}/api/v1/water/`
- **Headers:** `Authorization: Bearer {{token}}`
- **Body (JSON):**
```json
{
  "amount_ml": 750.0,
  "log_date": "2026-06-13",
  "notes": "Water bottle after gym"
}
```

#### Step 7: Check Dashboard
- **Method:** `GET`
- **URL:** `{{base_url}}/api/v1/users/dashboard`
- **Headers:** `Authorization: Bearer {{token}}`

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/fitness_tracker` |
| `SECRET_KEY` | JWT signing secret | `your-super-secret-key-change-this-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (minutes) | `30` |
| `APP_NAME` | Application display name | `Fitness Tracker API` |
| `APP_VERSION` | Application version | `1.0.0` |
| `DEBUG` | Enable debug mode | `True` |

---

## 🗃️ Database Schema

```
┌──────────────┐
│    users     │
├──────────────┤       ┌──────────────┐
│ id (PK)      │───┐   │   workouts   │
│ username     │   │   ├──────────────┤
│ email        │   ├──▶│ id (PK)      │
│ hashed_pass  │   │   │ user_id (FK) │
│ full_name    │   │   │ workout_name │
│ is_active    │   │   │ category     │
│ created_at   │   │   │ duration_min │
│ updated_at   │   │   │ calories     │
└──────────────┘   │   │ workout_date │
                   │   │ notes        │
                   │   └──────────────┘
                   │
                   │   ┌──────────────┐
                   │   │    goals     │
                   │   ├──────────────┤
                   ├──▶│ id (PK)      │
                   │   │ user_id (FK) │
                   │   │ goal_name    │
                   │   │ target_value │
                   │   │ current_val  │
                   │   │ deadline     │
                   │   │ is_achieved  │
                   │   └──────────────┘
                   │
                   │   ┌──────────────┐
                   │   │ weight_logs  │
                   │   ├──────────────┤
                   ├──▶│ id (PK)      │
                   │   │ user_id (FK) │
                   │   │ weight_kg    │
                   │   │ log_date     │
                   │   │ notes        │
                   │   └──────────────┘
                   │
                   │   ┌──────────────┐
                   │   │ water_logs   │
                   │   ├──────────────┤
                   └──▶│ id (PK)      │
                       │ user_id (FK) │
                       │ amount_ml    │
                       │ log_date     │
                       │ notes        │
                       └──────────────┘
```

**Relationships:**
- One **User** → Many **Workouts** (cascade delete)
- One **User** → Many **Goals** (cascade delete)
- One **User** → Many **Weight Logs** (cascade delete)
- One **User** → Many **Water Logs** (cascade delete)

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👤 Author

Fitness Tracker API — Built as a university final-year project demonstrating modern backend development with Python, FastAPI, and PostgreSQL.
