from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    url = settings.DATABASE_URL
    # asyncpg形式に正規化
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Neon は ?sslmode=require をURLに含むが asyncpg は connect_args で指定する必要がある
    ssl_needed = (
        "supabase.co" in url
        or "neon.tech" in url
        or "sslmode=require" in url
        or settings.DB_SSL
    )
    url = url.split("?")[0]  # クエリパラメータを除去
    connect_args = {"ssl": "require"} if ssl_needed else {}
    return create_async_engine(url, echo=False, connect_args=connect_args)


engine = _make_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
