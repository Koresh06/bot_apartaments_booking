from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.models.base import Base

if TYPE_CHECKING:
    from src.core.models import Users, Apartment

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    apartment_id: Mapped[int] = mapped_column(Integer, ForeignKey("apartments.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    user_rel: Mapped["Users"] = relationship("Users", back_populates="booking_rel")
    apartment_rel: Mapped["Apartment"] = relationship("Apartment", back_populates="booking_rel")
