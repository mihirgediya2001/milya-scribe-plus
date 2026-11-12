"""Request and response schemas for authentication."""

from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    clinic_name: str
    role: str  # admin | dentist | hygienist | coordinator | assistant


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Public-safe user representation."""

    id: str
    name: str
    email: str
    role: str
    clinic_id: str
    clinic_name: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut
