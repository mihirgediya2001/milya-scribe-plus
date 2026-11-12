"""Admin routes: user management and audit log for clinic admins."""

from fastapi import APIRouter

from app.dependencies import DB, require_permission
from app.models import AuditLog, User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(
    user=require_permission("manage_users"),
    db: DB = None,  # type: ignore[assignment]
):
    """List all users in the current clinic."""
    rows = (
        db.query(User)
        .filter(User.clinic_id == user.clinic_id)
        .order_by(User.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "role": r.role.value,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/audit")
def list_audit(
    user=require_permission("manage_users"),
    db: DB = None,  # type: ignore[assignment]
):
    """List recent audit log entries for the current clinic."""
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.clinic_id == user.clinic_id)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "action": r.action,
            "target_type": r.target_type,
            "target_id": r.target_id,
            "details": r.details,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
