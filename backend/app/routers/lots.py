from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, datetime, timezone

from app.db.base import get_db
from app.models import Lot, CageLot, Event
from app.models.event import EventType
from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas.lot import LotCreate, LotOut, LotMoveRequest, LotSplitRequest, LotMergeRequest

router = APIRouter(prefix="/lots", tags=["lots"])


@router.get("", response_model=list[LotOut])
async def list_lots(
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Lot).where(Lot.is_active == is_active))
    return result.scalars().all()


@router.get("/{lot_id}", response_model=LotOut)
async def get_lot(
    lot_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(404, "魚群が見つかりません")
    return lot


@router.post("", response_model=LotOut, status_code=201)
async def receive_lot(
    body: LotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lot = Lot(
        species=body.species,
        stage=body.stage,
        item_label=body.item_label,
        origin_type=body.origin_type,
        received_date=body.received_date,
        initial_count=body.initial_count,
        initial_avg_weight_g=body.initial_avg_weight_g,
        notes=body.notes,
        is_active=True,
    )
    db.add(lot)
    await db.flush()

    cage_lot = CageLot(
        cage_id=body.cage_id,
        lot_id=lot.id,
        start_date=body.received_date,
        start_count_est=body.initial_count,
        start_avg_weight_g=body.initial_avg_weight_g,
    )
    db.add(cage_lot)
    await db.commit()
    await db.refresh(lot)
    return lot


@router.post("/{lot_id}/move")
async def move_lot(
    lot_id: int,
    body: LotMoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(404, "魚群が見つかりません")

    # 現在のcage_lot を取得
    result2 = await db.execute(
        select(CageLot).where(CageLot.lot_id == lot_id, CageLot.end_date == None)
    )
    current_cl = result2.scalars().first()
    if not current_cl:
        raise HTTPException(400, "現在の配置情報が見つかりません")

    today = date.today()
    current_cl.end_date = today

    new_cl = CageLot(
        cage_id=body.to_cage_id,
        lot_id=lot_id,
        start_date=today,
        start_count_est=body.moved_count or current_cl.start_count_est,
        start_avg_weight_g=current_cl.start_avg_weight_g,
    )
    db.add(new_cl)

    event = Event(
        event_type=EventType.MOVE,
        occurred_at=datetime.now(timezone.utc),
        cage_id=current_cl.cage_id,
        lot_id=lot_id,
        user_id=current_user.id,
        payload_json={
            "from_cage_id": current_cl.cage_id,
            "to_cage_id": body.to_cage_id,
            "moved_count": body.moved_count,
            "memo": body.memo,
        },
    )
    db.add(event)
    await db.commit()
    return {"ok": True}


@router.post("/{lot_id}/split")
async def split_lot(
    lot_id: int,
    body: LotSplitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalar_one_or_none()
    if not lot:
        raise HTTPException(404, "魚群が見つかりません")

    result2 = await db.execute(
        select(CageLot).where(CageLot.lot_id == lot_id, CageLot.end_date == None)
    )
    current_cl = result2.scalars().first()
    if current_cl:
        current_cl.end_date = date.today()

    today = date.today()
    to_lot_ids = []
    alloc_counts = []

    for split in body.splits:
        new_lot = Lot(
            species=lot.species,
            stage=lot.stage,
            item_label=lot.item_label,
            origin_type=lot.origin_type,
            received_date=today,
            initial_count=split["count"],
            initial_avg_weight_g=lot.initial_avg_weight_g,
            is_active=True,
        )
        db.add(new_lot)
        await db.flush()
        to_lot_ids.append(new_lot.id)
        alloc_counts.append(split["count"])

        new_cl = CageLot(
            cage_id=split["cage_id"],
            lot_id=new_lot.id,
            start_date=today,
            start_count_est=split["count"],
            start_avg_weight_g=lot.initial_avg_weight_g,
        )
        db.add(new_cl)

    event = Event(
        event_type=EventType.SPLIT,
        occurred_at=datetime.now(timezone.utc),
        lot_id=lot_id,
        user_id=current_user.id,
        payload_json={
            "from_lot_id": lot_id,
            "to_lot_ids": to_lot_ids,
            "allocation_counts": alloc_counts,
            "memo": body.memo,
        },
    )
    db.add(event)
    lot.is_active = False
    await db.commit()
    return {"ok": True, "new_lot_ids": to_lot_ids}


@router.post("/merge")
async def merge_lots(
    body: LotMergeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    lots = []
    total_count = 0
    avg_weight_sum = 0.0

    for lid in body.from_lot_ids:
        result = await db.execute(select(Lot).where(Lot.id == lid))
        lot = result.scalar_one_or_none()
        if not lot:
            raise HTTPException(404, f"魚群 {lid} が見つかりません")
        lots.append(lot)
        total_count += lot.initial_count
        avg_weight_sum += lot.initial_avg_weight_g

    avg_weight = avg_weight_sum / len(lots) if lots else 0.0
    first = lots[0]
    merged = Lot(
        species=first.species,
        stage=first.stage,
        item_label=first.item_label,
        origin_type=first.origin_type,
        received_date=today,
        initial_count=total_count,
        initial_avg_weight_g=avg_weight,
        is_active=True,
    )
    db.add(merged)
    await db.flush()

    new_cl = CageLot(
        cage_id=body.target_cage_id,
        lot_id=merged.id,
        start_date=today,
        start_count_est=total_count,
        start_avg_weight_g=avg_weight,
    )
    db.add(new_cl)

    for lot in lots:
        result2 = await db.execute(
            select(CageLot).where(CageLot.lot_id == lot.id, CageLot.end_date == None)
        )
        for cl in result2.scalars().all():
            cl.end_date = today
        lot.is_active = False

    event = Event(
        event_type=EventType.MERGE,
        occurred_at=datetime.now(timezone.utc),
        lot_id=merged.id,
        user_id=current_user.id,
        payload_json={
            "from_lot_ids": body.from_lot_ids,
            "to_lot_id": merged.id,
        },
    )
    db.add(event)
    await db.commit()
    return {"ok": True, "merged_lot_id": merged.id}
