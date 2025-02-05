# Shared properties
from datetime import datetime
from typing import Annotated
from pydantic import Field
from pydantic.main import BaseModel


class CountryGeographyBase(BaseModel):
    name: Annotated[str, Field(examples=["Viet Nam"])]
    region_code: Annotated[str, Field(examples=["VN"])]


class CountryGeographyRead(CountryGeographyBase):
    id: int
    created_at: datetime


class CountryGeographyCreate(CountryGeographyBase):
    pass


class CountryGeographyUpdate(CountryGeographyBase):
    pass
