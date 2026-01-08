import os
import sys
from sqlalchemy.orm import Session

# Adjust path to import app package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash, generate_api_key
from app.models.database import User

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "lancxe.ceo@cyberguard.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")


def seed_admin(db: Session) -> User:
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if user:
        return user

    hashed_password = get_password_hash(ADMIN_PASSWORD)
    user = User(
        email=ADMIN_EMAIL,
        username=ADMIN_USERNAME,
        full_name="Admin User",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True,
        subscription_plan="unlimited",
        subscription_status="active",
        api_key=generate_api_key(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = seed_admin(db)
        print(f"Admin ready: {user.email} (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
