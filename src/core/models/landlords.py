from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.base import Base

if TYPE_CHECKING:
    from src.core.models import Users, Apartment


class Landlords(Base):
    __tablename__ = "landlords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(100))
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    user_rel: Mapped["Users"] = relationship("Users", back_populates="landlord_rel")
    apartment_rel: Mapped[List["Apartment"]] = relationship("Apartment", back_populates="landlord_rel", cascade="all, delete")
