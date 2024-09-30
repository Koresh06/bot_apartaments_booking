from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.base import Base

if TYPE_CHECKING:
    from src.core.models import Users, Apartment


class City(Base):
    __tablename__ = "citys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))

    apartment_rel: Mapped[List["Apartment"]] = relationship("Apartment", back_populates="city_rel")