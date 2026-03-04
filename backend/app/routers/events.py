from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import os
import uuid

from app.db.base import get_db
from app.models import Event, Attachment
from app.models.event import EventType
from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas.event import EventCreate, EventOut, SyncPushRequest, SyncPushResponse
from app.core.config import settings

router = APIRouter(tags=["events"])


@router.get("/events", response_model=list[EventOut])
async def list_events(
    cage_id: int | None = None,
    lot_id: int | None = None,
    event_type: str | None = None,
    from_: datetime | None = None,
    to: datetime | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Event).order_by(Event.occurred_at.desc()).limit(limit)
    if cage_id:
        q = q.where(Event.cage_id == cage_id)
    if lot_id:
        q = q.where(Event.lot_id == lot_id)
    if event_type:
        q = q.where(Event.event_type == event_type)
    if from_:
        q = q.where(Event.occurred_at >= from_)
    if to:
        q = q.where(Event.occurred_at <= to)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/events", response_model=EventOut, status_code=201)
async def create_event(
    body: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = Event(
        event_type=body.event_type,
        occurred_at=body.occurred_at,
        cage_id=body.cage_id,
        lot_id=body.lot_id,
        user_id=current_user.id,
        payload_json=body.payload_json,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/events/{event_id}/prev")
async def get_prev_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """同cage_id・同event_typeの直前イベントを返す（前回値コピー用）"""
    result = await db.execute(select(Event).where(Event.id == event_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(404, "イベントが見つかりません")
    q = (
        select(Event)
        .where(Event.cage_id == ev.cage_id)
        .where(Event.event_type == ev.event_type)
        .where(Event.id < event_id)
        .order_by(Event.occurred_at.desc())
        .limit(1)
    )
    result2 = await db.execute(q)
    prev = result2.scalar_one_or_none()
    return prev


@router.get("/events/last/{cage_id}/{event_type}")
async def get_last_event(
    cage_id: int,
    event_type: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """生簀の最新イベントを返す（前回値コピー用）"""
    q = (
        select(Event)
        .where(Event.cage_id == cage_id)
        .where(Event.event_type == event_type)
        .order_by(Event.occurred_at.desc())
        .limit(1)
    )
    result = await db.execute(q)
    ev = result.scalar_one_or_none()
    if not ev:
        return None
    return ev


@router.post("/events/{event_id}/attachments", status_code=201)
async def upload_attachment(
    event_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    ev = result.scalar_one_or_none()
    if not ev:
        raise HTTPException(404, "イベントが見つかりません")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "file")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    attachment = Attachment(
        event_id=event_id,
        file_url=f"/uploads/{filename}",
        file_type=file.content_type or "application/octet-stream",
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment


@router.post("/sync/push", response_model=SyncPushResponse)
async def sync_push(
    body: SyncPushRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """オフラインキューのバルク送信"""
    created_ids = []
    errors = []
    for i, ev_data in enumerate(body.events):
        try:
            event = Event(
                event_type=ev_data.event_type,
                occurred_at=ev_data.occurred_at,
                cage_id=ev_data.cage_id,
                lot_id=ev_data.lot_id,
                user_id=current_user.id,
                payload_json=ev_data.payload_json,
            )
            db.add(event)
            await db.flush()
            created_ids.append(event.id)
        except Exception as e:
            errors.append(f"item[{i}]: {str(e)}")
    await db.commit()
    return SyncPushResponse(created_ids=created_ids, errors=errors)


@router.get("/sync/pull")
async def sync_pull(
    since: datetime,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Event).where(Event.created_at > since).order_by(Event.created_at)
    )
    return result.scalars().all()
