from sqlalchemy import String, ForeignKey, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
import enum


class EventType(str, enum.Enum):
    FEEDING = "FEEDING"
    MORTALITY = "MORTALITY"
    SAMPLING = "SAMPLING"
    TREATMENT = "TREATMENT"
    ENVIRONMENT = "ENVIRONMENT"
    MOVE = "MOVE"
    SPLIT = "SPLIT"
    MERGE = "MERGE"
    HARVEST = "HARVEST"
    NOTE = "NOTE"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[EventType] = mapped_column(SAEnum(EventType))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cage_id: Mapped[int | None] = mapped_column(ForeignKey("cages.id"), nullable=True, index=True)
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("lots.id"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    cage: Mapped["Cage | None"] = relationship("Cage", back_populates="events")
    lot: Mapped["Lot | None"] = relationship("Lot", back_populates="events")
    user: Mapped["User"] = relationship("User", back_populates="events")
    attachments: Mapped[list["Attachment"]] = relationship("Attachment", back_populates="event")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    file_url: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    event: Mapped["Event"] = relationship("Event", back_populates="attachments")
