import sys
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password

def create_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.username == "testuser").first()
        if user:
            print("User already exists.")
            return

        new_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("TestPass123!"),
            full_name="Test User"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created: username=testuser, password=TestPass123!")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user()
