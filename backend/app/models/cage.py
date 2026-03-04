from sqlalchemy import String, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
import uuid


class Cage(Base):
    __tablename__ = "cages"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    size_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    size_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth: Mapped[float | None] = mapped_column(Float, nullable=True)
    qr_token: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, default=lambda: uuid.uuid4().hex
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    site: Mapped["Site"] = relationship("Site", back_populates="cages")
    cage_lots: Mapped[list["CageLot"]] = relationship("CageLot", back_populates="cage")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="cage")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="cage")
