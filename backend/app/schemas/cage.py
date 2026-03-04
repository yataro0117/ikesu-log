from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CageBase(BaseModel):
    name: str
    code: str
    site_id: int
    lat: Optional[float] = None
    lng: Optional[float] = None
    size_x: Optional[float] = None
    size_y: Optional[float] = None
    depth: Optional[float] = None
    is_active: bool = True


class CageCreate(CageBase):
    pass


class CagePatch(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    size_x: Optional[float] = None
    size_y: Optional[float] = None
    depth: Optional[float] = None
    is_active: Optional[bool] = None


class CageOut(CageBase):
    id: int
    qr_token: str
    created_at: datetime

    model_config = {"from_attributes": True}
