"""FastAPI dependency injection: database sessions, auth, and RBAC."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, UserRole


# ---------------------------------------------------------------------------
# Database session
# ---------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Current user (token-based)
# ---------------------------------------------------------------------------

def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the Bearer token to a User, or 401."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing auth token")

    token = authorization.removeprefix("Bearer ").strip()
    user = db.query(User).filter(User.session_token == token).first()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------------------------------------------------------------------------
# Role-based access control
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN: {
        "record", "review", "edit", "approve", "finalize",
        "manage_templates", "manage_users",
    },
    UserRole.DENTIST: {
        "record", "review", "edit", "approve", "finalize",
        "manage_templates",
    },
    UserRole.ASSISTANT: {"record", "review"},
}


def require_permission(permission: str):
    """Return a dependency that 403s if the user lacks *permission*."""

    def _check(
        authorization: str = Header(default=""),
        db: Session = Depends(get_db),
    ) -> User:
        user = get_current_user(authorization=authorization, db=db)
        allowed = ROLE_PERMISSIONS.get(user.role, set())
        if permission not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Role '{user.role.value}' cannot '{permission}'",
            )
        return user

    return Depends(_check)
