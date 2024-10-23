# Shared properties
from datetime import datetime
from typing import Annotated, Optional
from pydantic import Field
from pydantic.main import BaseModel


# Shared properties
class GroupUserBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50, examples=["Supper Admin"])]
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RelateGroupUserSchema(BaseModel):
    name: Optional[str] = None


class GroupUserInDBBase(GroupUserBase):
    id: int
