from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.lot import Species, Stage, OriginType


class LotCreate(BaseModel):
    species: Species
    stage: Stage
    item_label: str
    origin_type: OriginType = OriginType.WILD
    received_date: date
    initial_count: int
    initial_avg_weight_g: float = 0.0
    cage_id: int  # 最初の配置先
    notes: Optional[str] = None


class LotOut(BaseModel):
    id: int
    species: str
    stage: str
    item_label: str
    origin_type: str
    received_date: date
    initial_count: int
    initial_avg_weight_g: float
    notes: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class LotMoveRequest(BaseModel):
    to_cage_id: int
    moved_count: Optional[int] = None
    memo: Optional[str] = None


class LotSplitRequest(BaseModel):
    splits: list[dict]  # [{cage_id: int, count: int}]
    memo: Optional[str] = None


class LotMergeRequest(BaseModel):
    from_lot_ids: list[int]
    target_cage_id: int
    memo: Optional[str] = None
