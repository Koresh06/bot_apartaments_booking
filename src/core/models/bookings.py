from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.base import Base

if TYPE_CHECKING:
    from src.core.models import Users, Apartment

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    apartment_id: Mapped[int] = mapped_column(Integer, ForeignKey("apartments.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    user_rel: Mapped["Users"] = relationship("Users", back_populates="booking_rel")
    apartment_rel: Mapped["Apartment"] = relationship("Apartment", back_populates="booking_rel")
