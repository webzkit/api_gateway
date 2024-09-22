from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    user_group_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
