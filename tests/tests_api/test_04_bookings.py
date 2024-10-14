from datetime import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.apmin_panel.api.services.booking_api_service import BookingApiRepo
from src.core.models import Booking, Apartment, City
from ..conftest import async_session_maker


async def test_get_bookings(
    authenticated_client: AsyncClient, prepare_database
):
    async with async_session_maker() as session:
        city = City(
            id=1,
            name="City",
        )
        session.add(city)

        apartment = Apartment(
            id=1,
            landlord_id=1,
            city_id=1,
            street="Street",
            house_number=1,
            apartment_number=1,
            price_per_day=1000,
            rooms=1,
            is_available=True,
            description="Description",
            rating=1,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        session.add(apartment)

        booking = Booking(
            id=1,
            user_id=1,
            apartment_id=1,
            start_date=datetime.now(),
            end_date=datetime.now(),
            is_confirmed=False,
            is_completed=False,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)

        booking_from_db: Booking = await BookingApiRepo(session).get_all_bookings()

        assert booking_from_db[0].id == booking.id
        assert booking_from_db[0].user_id == booking.user_id
        assert booking_from_db[0].apartment_id == booking.apartment_id
        assert booking_from_db[0].start_date == booking.start_date
        assert booking_from_db[0].end_date == booking.end_date
        assert booking_from_db[0].is_confirmed == booking.is_confirmed
        assert booking_from_db[0].is_completed == booking.is_completed
        assert booking_from_db[0].create_at == booking.create_at
        assert booking_from_db[0].update_at == booking.update_at

    response = await authenticated_client.get("/booking/get-bookings/")
    assert response.status_code == 200






