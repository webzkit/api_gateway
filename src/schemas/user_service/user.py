from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field
import uuid as uuid_pkg


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(examples=["info@zkit.com"])]
    password: Annotated[
        str,
        Field(
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            examples=["123456"],
        ),
    ]


class RefreshTokenRequest(BaseModel):
    token: Annotated[str, Field(default="")]


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserRead(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    group_id: int
    group_name: str
    uuid: uuid_pkg.UUID


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[
        str,
        Field(
            min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"]
        ),
    ]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[
        str,
        Field(
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            examples=["Str1ngst!"],
        ),
    ]


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str | None,
        Field(min_length=2, max_length=30, examples=["User Userberg"], default=None),
    ]
