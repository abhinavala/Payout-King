"""
Authentication schemas.
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    created_at: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for access token."""

    access_token: str
    token_type: str

