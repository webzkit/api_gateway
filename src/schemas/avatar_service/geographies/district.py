from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class DisctricGeographyBase(BaseModel):
    name: Annotated[str, Field(examples=["Quan 1"])]
    geography_province_id: Annotated[int, Field(examples=[1])]


class DistrictGeographyRead(DisctricGeographyBase):
    id: int
    created_at: datetime


class DistrictGeographyCreate(DisctricGeographyBase):
    pass


class DistrictGeographyUpdate(DisctricGeographyBase):
    pass
