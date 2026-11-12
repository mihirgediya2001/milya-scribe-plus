"""Authentication helpers: password hashing and user lifecycle."""

import uuid

import bcrypt
from sqlalchemy.orm import Session

from app.models import Clinic, User, UserRole


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# User lifecycle
# ---------------------------------------------------------------------------

def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    clinic_name: str,
    role: str,
) -> tuple[User, str]:
    """Register a new user. Creates the clinic if it doesn't exist yet.

    Returns the User row and a fresh session token.
    Raises ``ValueError`` if the email is already taken.
    """
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email already registered")

    clinic = db.query(Clinic).filter(Clinic.name == clinic_name).first()
    if clinic is None:
        clinic = Clinic(name=clinic_name)
        db.add(clinic)
        db.flush()

    token = str(uuid.uuid4())
    user = User(
        clinic_id=clinic.id,
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=UserRole(role),
        session_token=token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, token


def authenticate_user(db: Session, *, email: str, password: str) -> tuple[User, str]:
    """Verify credentials and issue a new session token.

    Raises ``ValueError`` on bad email or password.
    """
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    token = str(uuid.uuid4())
    user.session_token = token
    db.commit()
    return user, token
