import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.models import User, Farm, Site, Cage, Lot, CageLot
from app.models.user import UserRole
from app.models.lot import Species, Stage, OriginType
from app.core.security import get_password_hash
from datetime import date
import uuid

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_data(db_session):
    """最小限のテスト用データ"""
    user = User(
        name="テスト管理者",
        email="test@example.com",
        password_hash=get_password_hash("testpass"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.flush()

    farm = Farm(name="テスト養殖場")
    db_session.add(farm)
    await db_session.flush()

    site = Site(farm_id=farm.id, name="テストサイト")
    db_session.add(site)
    await db_session.flush()

    cage = Cage(
        site_id=site.id,
        name="テスト生簀01",
        code="TEST-01",
        qr_token=uuid.uuid4().hex,
        is_active=True,
    )
    db_session.add(cage)
    await db_session.flush()

    lot = Lot(
        species=Species.BURI,
        stage=Stage.HAMACHI,
        item_label="ハマチ",
        origin_type=OriginType.WILD,
        received_date=date(2025, 10, 1),
        initial_count=1000,
        initial_avg_weight_g=500.0,
        is_active=True,
    )
    db_session.add(lot)
    await db_session.flush()

    cage_lot = CageLot(
        cage_id=cage.id,
        lot_id=lot.id,
        start_date=date(2025, 10, 1),
        start_count_est=1000,
        start_avg_weight_g=500.0,
    )
    db_session.add(cage_lot)
    await db_session.commit()

    return {"user": user, "farm": farm, "site": site, "cage": cage, "lot": lot}
