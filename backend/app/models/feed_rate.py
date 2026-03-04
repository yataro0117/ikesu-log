from sqlalchemy import String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from .lot import Species, Stage


class FeedRateRule(Base):
    __tablename__ = "feed_rate_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    species: Mapped[Species] = mapped_column(SAEnum(Species))
    stage: Mapped[Stage] = mapped_column(SAEnum(Stage))
    temp_min: Mapped[float] = mapped_column(Float)
    temp_max: Mapped[float] = mapped_column(Float)
    feed_rate_pct_per_day: Mapped[float] = mapped_column(Float)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[int] = mapped_column(default=0)
