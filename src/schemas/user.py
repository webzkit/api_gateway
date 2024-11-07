from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field

from .group import RelateGroupUserSchema


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserRead(BaseModel):
    id: int

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[
        str,
        Field(
            min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"]
        )
    ]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    group_id: int
    group_name: str


