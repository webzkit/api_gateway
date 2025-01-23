# Shared properties
from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class WardGeographyBase(BaseModel):
    name: Annotated[str, Field(examples=["Phuong 1"])]
    geography_district_id: Annotated[int, Field(examples=[1])]


class WardGeographyRead(WardGeographyBase):
    id: int
    created_at: datetime


class WardGeographyCreate(WardGeographyBase):
    pass


class WardGeographyUpdate(WardGeographyBase):
    pass
