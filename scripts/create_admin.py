"""
Script to create an admin user in the database.
Usage: python scripts/create_admin.py <email> <password>
"""
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.common import UserStatus

def create_admin_user(email: str, password: str, timezone: str = "UTC"):
    """Create an admin user in the database."""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            if not existing_user.is_admin:
                # Make them admin
                existing_user.is_admin = True
                db.commit()
                print(f"User {email} has been promoted to admin!")
            else:
                print(f"User {email} is already an admin.")
            return
        
        # Create new admin user
        password_hash = get_password_hash(password)
        admin_user = User(
            email=email,
            password_hash=password_hash,
            timezone=timezone,
            status=UserStatus.ACTIVE,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✓ Admin user created successfully!")
        print(f"  Email: {email}")
        print(f"  ID: {admin_user.id}")
        print(f"\nYou can now login with these credentials at /api/v1/auth/login")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_admin.py <email> <password> [timezone]")
        print("Example: python scripts/create_admin.py admin@example.com SecurePass123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    timezone = sys.argv[3] if len(sys.argv) > 3 else "UTC"
    
    create_admin_user(email, password, timezone)
