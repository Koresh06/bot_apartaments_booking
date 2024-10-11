from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.models.base import Base

if TYPE_CHECKING:
    from src.core.models import Landlords, Booking, ApartmentPhoto, City


class Apartment(Base):
    __tablename__ = "apartments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    landlord_id: Mapped[int] = mapped_column(Integer, ForeignKey("landlords.id"), nullable=False)
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("citys.id"))
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    house_number: Mapped[int] = mapped_column(Integer, nullable=False)
    apartment_number: Mapped[int] = mapped_column(Integer, nullable=True)
    price_per_day: Mapped[float] = mapped_column(Float, nullable=False)
    rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    landlord_rel: Mapped["Landlords"] = relationship("Landlords", back_populates="apartment_rel")
    booking_rel: Mapped[List["Booking"]] = relationship("Booking", back_populates="apartment_rel", cascade="all, delete")
    photos_rel: Mapped[List["ApartmentPhoto"]] = relationship("ApartmentPhoto", back_populates="apartment_rel", cascade="all, delete")
    city_rel: Mapped["City"] = relationship("City", back_populates="apartment_rel") 

