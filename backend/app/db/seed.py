"""Seed initial data for ikesu_log"""
import asyncio
import uuid
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import User, Farm, Site, Cage, Lot, CageLot, FeedRateRule
from app.models.user import UserRole
from app.models.lot import Species, Stage, OriginType


async def seed(session: AsyncSession) -> None:
    # Users
    admin = User(
        name="管理者",
        email="admin@ikesu.local",
        password_hash=get_password_hash("admin1234"),
        role=UserRole.ADMIN,
    )
    worker = User(
        name="現場太郎",
        email="worker@ikesu.local",
        password_hash=get_password_hash("worker1234"),
        role=UserRole.WORKER,
    )
    session.add_all([admin, worker])
    await session.flush()

    # Farm & Site
    farm = Farm(name="第一養殖場")
    session.add(farm)
    await session.flush()

    site = Site(
        farm_id=farm.id,
        name="沖合いけす群A",
        location_text="長崎県五島列島沖",
        lat=32.7,
        lng=129.0,
    )
    session.add(site)
    await session.flush()

    # Cages (10台)
    cage_data = [
        {"name": f"いけす{i:02d}", "code": f"CAGE-{i:02d}",
         "lat": 32.7 + (i % 4) * 0.001, "lng": 129.0 + (i // 4) * 0.001}
        for i in range(1, 11)
    ]
    cages = []
    for d in cage_data:
        c = Cage(
            site_id=site.id,
            name=d["name"],
            code=d["code"],
            lat=d["lat"],
            lng=d["lng"],
            size_x=20.0,
            size_y=20.0,
            depth=8.0,
            qr_token=uuid.uuid4().hex,
            is_active=True,
        )
        session.add(c)
        cages.append(c)
    await session.flush()

    # Lots
    lots_data = [
        {
            "species": Species.BURI, "stage": Stage.HAMACHI,
            "item_label": "ハマチ", "initial_count": 3000,
            "initial_avg_weight_g": 500.0, "received_date": date(2025, 10, 1),
        },
        {
            "species": Species.BURI, "stage": Stage.BURI,
            "item_label": "ブリ", "initial_count": 2000,
            "initial_avg_weight_g": 2500.0, "received_date": date(2025, 6, 1),
        },
        {
            "species": Species.KAMPACHI, "stage": Stage.HAMACHI,
            "item_label": "カンパチ", "initial_count": 1500,
            "initial_avg_weight_g": 800.0, "received_date": date(2025, 9, 1),
        },
        {
            "species": Species.BURI, "stage": Stage.MOJAKO,
            "item_label": "モジャコ", "initial_count": 5000,
            "initial_avg_weight_g": 30.0, "received_date": date(2026, 2, 1),
        },
    ]
    lots = []
    for d in lots_data:
        lot = Lot(
            species=d["species"],
            stage=d["stage"],
            item_label=d["item_label"],
            origin_type=OriginType.WILD,
            received_date=d["received_date"],
            initial_count=d["initial_count"],
            initial_avg_weight_g=d["initial_avg_weight_g"],
            is_active=True,
        )
        session.add(lot)
        lots.append(lot)
    await session.flush()

    # CageLots: 各生簀に魚群を割り当て
    cage_lot_assignments = [
        (0, 0), (1, 0), (2, 0),   # cages 1-3: ハマチ
        (3, 1), (4, 1),            # cages 4-5: ブリ
        (5, 2), (6, 2),            # cages 6-7: カンパチ
        (7, 3), (8, 3), (9, 3),    # cages 8-10: モジャコ
    ]
    for cage_idx, lot_idx in cage_lot_assignments:
        lot = lots[lot_idx]
        cl = CageLot(
            cage_id=cages[cage_idx].id,
            lot_id=lot.id,
            start_date=lot.received_date,
            start_count_est=lot.initial_count // 3,
            start_avg_weight_g=lot.initial_avg_weight_g,
        )
        session.add(cl)

    # Feed rate rules
    feed_rules = [
        FeedRateRule(species=Species.BURI, stage=Stage.MOJAKO, temp_min=10, temp_max=15, feed_rate_pct_per_day=3.0),
        FeedRateRule(species=Species.BURI, stage=Stage.MOJAKO, temp_min=15, temp_max=25, feed_rate_pct_per_day=4.0),
        FeedRateRule(species=Species.BURI, stage=Stage.HAMACHI, temp_min=10, temp_max=15, feed_rate_pct_per_day=1.5),
        FeedRateRule(species=Species.BURI, stage=Stage.HAMACHI, temp_min=15, temp_max=25, feed_rate_pct_per_day=2.5),
        FeedRateRule(species=Species.BURI, stage=Stage.BURI, temp_min=10, temp_max=20, feed_rate_pct_per_day=1.0),
        FeedRateRule(species=Species.BURI, stage=Stage.BURI, temp_min=20, temp_max=28, feed_rate_pct_per_day=1.5),
        FeedRateRule(species=Species.KAMPACHI, stage=Stage.HAMACHI, temp_min=18, temp_max=28, feed_rate_pct_per_day=2.0),
    ]
    session.add_all(feed_rules)
    await session.commit()
    print("Seed completed successfully.")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy import select
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            print("Already seeded, skipping.")
            return
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
