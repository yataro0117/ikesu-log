from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from app.models.event import EventType


class EventCreate(BaseModel):
    event_type: EventType
    occurred_at: datetime
    cage_id: Optional[int] = None
    lot_id: Optional[int] = None
    payload_json: dict = {}


class EventOut(BaseModel):
    id: int
    event_type: str
    occurred_at: datetime
    cage_id: Optional[int]
    lot_id: Optional[int]
    user_id: int
    payload_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncPushRequest(BaseModel):
    events: list[EventCreate]


class SyncPushResponse(BaseModel):
    created_ids: list[int]
    errors: list[str] = []
