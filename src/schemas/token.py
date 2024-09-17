from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class TokenPayload(BaseModel):
    payload: Optional[dict] = None


# Shared properties
class TokenBase(BaseModel):
    client_id: Optional[str] = None
    access_token: str
    refresh_token: str
    expires: Optional[datetime] = None
    last_active: Optional[datetime] = None
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Properties to receive via API on creation
class CreateTokenSchema(TokenBase):
    access_token: str
    refresh_token: str
    user_id: int


# Properties to receive via API on creation
class UpdateTokenSchema(TokenBase):
    access_token: str
    refresh_token: str
