# Shared properties
from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel

class GroupBase(BaseModel):
    name: Annotated[str, Field(examples=["free"])]


class GroupRead(GroupBase):
    id: int
    created_at: datetime


class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    pass

