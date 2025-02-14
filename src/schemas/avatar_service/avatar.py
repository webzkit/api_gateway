from typing import Annotated, Any, List, Optional
from pydantic import BaseModel, EmailStr, Field


class AvatarBase(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(
        default=None, min_length=10, max_length=15, pattern=r"^\d*$"
    )
    firstname: Annotated[str, Field(default="firstName")]
    lastname: Annotated[str, Field(default="lastName")]
    is_kol: Annotated[bool, Field(default=False)]


class AvatarCreate(AvatarBase):
    sectors: Annotated[List[Any], Field(default=[1])]
    pass


class AvatarUpdate(AvatarBase):
    pass
