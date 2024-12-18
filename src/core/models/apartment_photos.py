from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base

if TYPE_CHECKING:
    from src.core.models import Apartment


class ApartmentPhoto(Base):
    __tablename__ = "apartment_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    apartment_id: Mapped[int] = mapped_column(Integer, ForeignKey("apartments.id"), nullable=False)
    photos_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    apartment_rel: Mapped["Apartment"] = relationship("Apartment", back_populates="photos_rel")
