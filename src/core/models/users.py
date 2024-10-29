from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.models.base import Base

if TYPE_CHECKING:
    from src.core.models import Landlords, Booking


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    booking_rel: Mapped[List["Booking"]] = relationship("Booking", back_populates="user_rel", cascade="all, delete")
    landlord_rel: Mapped["Landlords"] = relationship("Landlords", uselist=False, back_populates="user_rel", cascade="all, delete")