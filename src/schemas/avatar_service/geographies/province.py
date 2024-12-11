# Shared properties
from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class ProvinceGegraphyBase(BaseModel):
    name: Annotated[str, Field(examples=["free"])]


class ProvinceGeographyRead(ProvinceGegraphyBase):
    id: int
    created_at: datetime


class ProvinceGeographyCreate(ProvinceGegraphyBase):
    pass


class ProvinceGeographyUpdate(ProvinceGegraphyBase):
    pass
