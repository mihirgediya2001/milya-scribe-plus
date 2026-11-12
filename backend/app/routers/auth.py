"""Authentication routes: sign-up, login, and current-user check."""

from fastapi import APIRouter, HTTPException

from app.dependencies import DB, CurrentUser
from app.schemas.auth import AuthResponse, LoginRequest, SignUpRequest, UserOut
from app.services.auth import authenticate_user, create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_out(user) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        clinic_id=user.clinic_id,
        clinic_name=user.clinic.name,
    )


@router.post("/signup", response_model=AuthResponse)
def signup(req: SignUpRequest, db: DB) -> AuthResponse:
    try:
        user, token = create_user(
            db,
            name=req.name,
            email=req.email,
            password=req.password,
            clinic_name=req.clinic_name,
            role=req.role,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return AuthResponse(token=token, user=_user_out(user))


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: DB) -> AuthResponse:
    try:
        user, token = authenticate_user(db, email=req.email, password=req.password)
    except ValueError as exc:
        raise HTTPException(401, str(exc))
    return AuthResponse(token=token, user=_user_out(user))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> UserOut:
    return _user_out(user)
