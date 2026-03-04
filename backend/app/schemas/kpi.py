from pydantic import BaseModel
from typing import Optional


class CageKPI(BaseModel):
    cage_id: int
    cage_name: str
    lot_id: Optional[int]
    item_label: Optional[str]
    est_count: int
    est_avg_weight_g: float
    est_biomass_kg: float
    mortality_rate_7d: Optional[float]  # %
    fcr_14d: Optional[float]
    sgr: Optional[float]  # %/day
    days_to_target: Optional[int]
    target_weight_g: float = 5000.0
    is_fcr_estimated: bool = True
    data_quality: str = "ok"  # ok / insufficient


class SiteSummary(BaseModel):
    site_id: int
    site_name: str
    total_biomass_kg: float
    total_est_count: int
    cage_count: int
    active_lot_count: int
    cages: list[CageKPI]


class TodayTodoItem(BaseModel):
    cage_id: int
    cage_name: str
    item_label: Optional[str]
    missing_types: list[str]  # ["FEEDING", "ENVIRONMENT"]
    last_feeding_at: Optional[str]
