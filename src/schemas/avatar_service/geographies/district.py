# Shared properties
from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class DistrictGegraphyBase(BaseModel):
    name: Annotated[str, Field(examples=["Quan 1"])]
    geography_province_id: Annotated[int, Field(examples=[1])]


class DistrictGeographyRead(DistrictGegraphyBase):
    id: int
    created_at: datetime


class DistrictGeographyCreate(DistrictGegraphyBase):
    pass


class DistrictGeographyUpdate(DistrictGegraphyBase):
    pass
