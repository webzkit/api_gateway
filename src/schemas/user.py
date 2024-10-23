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


# Shared properties
class UserBase(BaseModel):
    email: Annotated[EmailStr, Field(examples=["info@zkit.com"])]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Annotated[
        str | None,
        Field(min_length=3, max_length=50, examples=["Full name"], default=None),
    ]
    user_group_id: Annotated[int, Field(examples=[1])]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserInDB(UserBase):
    id: int
    group: RelateGroupUserSchema


class CreateUserSchema(UserBase):
    password: Annotated[
        str,
        Field(
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            examples=["Pa$$w0rd"],
        ),
    ]


class UpdateUserSchema(BaseModel):
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Annotated[
        str | None,
        Field(min_length=3, max_length=50, examples=["Full name"], default=None),
    ]
    user_group_id: Annotated[int, Field(examples=[1])]


class UserResponse(UserInDB):
    pass
