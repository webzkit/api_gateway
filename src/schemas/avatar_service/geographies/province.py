# Shared properties
from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class ProvinceGeographyBase(BaseModel):
    name: Annotated[str, Field(examples=["TP Ho Chi Minh"])]


class ProvinceGeographyRead(ProvinceGeographyBase):
    id: int
    created_at: datetime


class ProvinceGeographyCreate(ProvinceGeographyBase):
    pass


class ProvinceGeographyUpdate(ProvinceGeographyBase):
    pass
