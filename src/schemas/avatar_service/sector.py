from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class SectorBase(BaseModel):
    name: Annotated[str, Field(examples=["Social"])]


class SectorRead(SectorBase):
    id: int
    created_at: datetime


class SectorCreate(SectorBase):
    pass


class SectorUpdate(SectorBase):
    pass
