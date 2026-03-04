"""KPI calculation service for ikesu_log"""
import math
from datetime import datetime, timedelta, date, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Cage, CageLot, Lot, Event, Site
from app.models.event import EventType
from app.schemas.kpi import CageKPI, SiteSummary, TodayTodoItem

TARGET_WEIGHT_G = 5000.0


async def calc_cage_kpi(cage: Cage, db: AsyncSession) -> CageKPI:
    """生簀ごとのKPIを計算"""
    now = datetime.now(timezone.utc)
    today = now.date()

    # 現在の cage_lot を取得
    result = await db.execute(
        select(CageLot)
        .where(CageLot.cage_id == cage.id)
        .where(CageLot.end_date == None)
        .order_by(CageLot.start_date.desc())
        .limit(1)
    )
    cage_lot = result.scalar_one_or_none()

    if not cage_lot:
        return CageKPI(
            cage_id=cage.id, cage_name=cage.name,
            lot_id=None, item_label=None,
            est_count=0, est_avg_weight_g=0, est_biomass_kg=0,
            mortality_rate_7d=None, fcr_14d=None, sgr=None,
            days_to_target=None, data_quality="no_lot",
        )

    lot_id = cage_lot.lot_id
    result_lot = await db.execute(select(Lot).where(Lot.id == lot_id))
    lot = result_lot.scalar_one_or_none()

    # 推定尾数計算
    start_count = cage_lot.start_count_est

    # 累積死亡
    mortality_result = await db.execute(
        select(func.sum(Event.payload_json["dead_count"].as_integer()))
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.MORTALITY)
        .where(Event.occurred_at >= datetime.combine(cage_lot.start_date, datetime.min.time()))
    )
    total_mortality = mortality_result.scalar() or 0

    # 出荷尾数
    harvest_result = await db.execute(
        select(func.sum(Event.payload_json["harvest_count"].as_integer()))
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.HARVEST)
        .where(Event.occurred_at >= datetime.combine(cage_lot.start_date, datetime.min.time()))
    )
    total_harvest_count = harvest_result.scalar() or 0

    est_count = max(0, start_count - total_mortality - total_harvest_count)

    # 最新サンプリング体重
    sampling_result = await db.execute(
        select(Event)
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.SAMPLING)
        .order_by(Event.occurred_at.desc())
        .limit(1)
    )
    latest_sampling = sampling_result.scalar_one_or_none()
    est_avg_weight_g = (
        latest_sampling.payload_json.get("avg_weight_g", cage_lot.start_avg_weight_g)
        if latest_sampling
        else cage_lot.start_avg_weight_g
    )

    est_biomass_kg = (est_count * est_avg_weight_g) / 1000.0

    # 死亡率(7日)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    mort_7d_result = await db.execute(
        select(func.sum(Event.payload_json["dead_count"].as_integer()))
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.MORTALITY)
        .where(Event.occurred_at >= seven_days_ago)
    )
    mort_7d = mort_7d_result.scalar() or 0
    mortality_rate_7d = (mort_7d / max(est_count + mort_7d, 1)) * 100

    # 簡易FCR(14日)
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
    feed_result = await db.execute(
        select(func.sum(Event.payload_json["feed_kg"].as_float()))
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.FEEDING)
        .where(Event.occurred_at >= fourteen_days_ago)
    )
    feed_14d = feed_result.scalar() or 0.0

    # 14日前後のサンプリング
    sampling_before = await db.execute(
        select(Event)
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.SAMPLING)
        .where(Event.occurred_at >= fourteen_days_ago)
        .order_by(Event.occurred_at.asc())
        .limit(1)
    )
    samp_before = sampling_before.scalar_one_or_none()
    sampling_after = latest_sampling

    fcr_14d = None
    is_fcr_estimated = True
    if samp_before and sampling_after and samp_before.id != sampling_after.id:
        w1 = samp_before.payload_json.get("avg_weight_g", 0)
        w2 = sampling_after.payload_json.get("avg_weight_g", 0)
        n = (samp_before.payload_json.get("sample_count", est_count) + est_count) / 2
        growth_kg = (w2 - w1) * n / 1000.0
        if growth_kg > 0 and feed_14d > 0:
            fcr_14d = feed_14d / growth_kg
            is_fcr_estimated = False

    # SGR (直近2サンプリング)
    sgr = None
    sampling_prev_result = await db.execute(
        select(Event)
        .where(Event.cage_id == cage.id)
        .where(Event.event_type == EventType.SAMPLING)
        .order_by(Event.occurred_at.desc())
        .limit(2)
    )
    samplings = sampling_prev_result.scalars().all()
    if len(samplings) >= 2:
        s1, s2 = samplings[1], samplings[0]  # older first
        w1 = s1.payload_json.get("avg_weight_g", 1)
        w2 = s2.payload_json.get("avg_weight_g", 1)
        days = max((s2.occurred_at - s1.occurred_at).days, 1)
        if w1 > 0 and w2 > 0:
            sgr = (math.log(w2) - math.log(w1)) / days * 100

    # 出荷見込み日
    days_to_target = None
    if sgr and sgr > 0 and est_avg_weight_g > 0 and est_avg_weight_g < TARGET_WEIGHT_G:
        days_to_target = int(
            (math.log(TARGET_WEIGHT_G) - math.log(est_avg_weight_g)) / (sgr / 100)
        )

    data_quality = "ok" if est_count > 0 else "insufficient"

    return CageKPI(
        cage_id=cage.id,
        cage_name=cage.name,
        lot_id=lot_id,
        item_label=lot.item_label if lot else None,
        est_count=est_count,
        est_avg_weight_g=est_avg_weight_g,
        est_biomass_kg=est_biomass_kg,
        mortality_rate_7d=round(mortality_rate_7d, 2),
        fcr_14d=round(fcr_14d, 2) if fcr_14d else None,
        sgr=round(sgr, 3) if sgr else None,
        days_to_target=days_to_target,
        is_fcr_estimated=is_fcr_estimated,
        data_quality=data_quality,
    )


async def calc_today_todos(db: AsyncSession) -> list[TodayTodoItem]:
    """今日給餌未入力の生簀を抽出"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(select(Cage).where(Cage.is_active == True))
    cages = result.scalars().all()

    todos = []
    for cage in cages:
        # 今日のFEEDINGイベントを確認
        feeding_result = await db.execute(
            select(Event)
            .where(Event.cage_id == cage.id)
            .where(Event.event_type == EventType.FEEDING)
            .where(Event.occurred_at >= today_start)
        )
        today_feeding = feeding_result.scalar_one_or_none()

        missing = []
        if not today_feeding:
            missing.append("FEEDING")

        # 現在のlot_idを取得
        cl_result = await db.execute(
            select(CageLot)
            .where(CageLot.cage_id == cage.id)
            .where(CageLot.end_date == None)
            .limit(1)
        )
        cl = cl_result.scalar_one_or_none()
        lot_id = cl.lot_id if cl else None
        item_label = None
        if cl:
            lot_res = await db.execute(select(Lot).where(Lot.id == cl.lot_id))
            lot_obj = lot_res.scalar_one_or_none()
            item_label = lot_obj.item_label if lot_obj else None

        # 最終給餌日時
        last_feed_result = await db.execute(
            select(Event)
            .where(Event.cage_id == cage.id)
            .where(Event.event_type == EventType.FEEDING)
            .order_by(Event.occurred_at.desc())
            .limit(1)
        )
        last_feed = last_feed_result.scalar_one_or_none()
        last_feeding_at = last_feed.occurred_at.isoformat() if last_feed else None

        if missing:
            todos.append(TodayTodoItem(
                cage_id=cage.id,
                cage_name=cage.name,
                item_label=item_label,
                missing_types=missing,
                last_feeding_at=last_feeding_at,
            ))

    return todos
