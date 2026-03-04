from sqlalchemy import String, ForeignKey, Float, Boolean, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from app.db.base import Base
import enum


class Species(str, enum.Enum):
    BURI = "BURI"
    KAMPACHI = "KAMPACHI"


class Stage(str, enum.Enum):
    MOJAKO = "MOJAKO"
    HAMACHI = "HAMACHI"
    BURI = "BURI"


class OriginType(str, enum.Enum):
    WILD = "WILD"
    HATCHERY = "HATCHERY"
    TRANSFER = "TRANSFER"


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(primary_key=True)
    species: Mapped[Species] = mapped_column(SAEnum(Species))
    stage: Mapped[Stage] = mapped_column(SAEnum(Stage))
    item_label: Mapped[str] = mapped_column(String(50))
    origin_type: Mapped[OriginType] = mapped_column(SAEnum(OriginType), default=OriginType.WILD)
    received_date: Mapped[date] = mapped_column(Date)
    initial_count: Mapped[int]
    initial_avg_weight_g: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    cage_lots: Mapped[list["CageLot"]] = relationship("CageLot", back_populates="lot")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="lot")


class CageLot(Base):
    __tablename__ = "cage_lots"

    id: Mapped[int] = mapped_column(primary_key=True)
    cage_id: Mapped[int] = mapped_column(ForeignKey("cages.id"))
    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_count_est: Mapped[int]
    end_count_est: Mapped[int | None] = mapped_column(nullable=True)
    start_avg_weight_g: Mapped[float] = mapped_column(Float, default=0.0)
    end_avg_weight_g: Mapped[float | None] = mapped_column(Float, nullable=True)

    cage: Mapped["Cage"] = relationship("Cage", back_populates="cage_lots")
    lot: Mapped["Lot"] = relationship("Lot", back_populates="cage_lots")
