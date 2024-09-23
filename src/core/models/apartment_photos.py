from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.base import Base

if TYPE_CHECKING:
    from src.core.models import Apartment


class ApartmentPhoto(Base):
    __tablename__ = "apartment_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    apartment_id: Mapped[int] = mapped_column(Integer, ForeignKey("apartments.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    apartment_rel: Mapped["Apartment"] = relationship("Apartment", back_populates="photos_rel")
