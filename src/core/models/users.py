from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.base import Base

if TYPE_CHECKING:
    from src.core.models import Landlords, Booking




class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    booking_rel: Mapped[List["Booking"]] = relationship("Booking", back_populates="user_rel", cascade="all, delete")
    landlord_rel: Mapped["Landlords"] = relationship("Landlords", uselist=False, back_populates="user_rel")