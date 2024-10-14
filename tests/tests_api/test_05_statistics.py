from datetime import datetime, date
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.apmin_panel.api.services.statistics_api_service import StatisticsApiRepo
from src.core.models import Booking, Apartment, City
from ..conftest import async_session_maker


async def test_get_statistics(authenticated_client: AsyncClient, prepare_database):
    response = await authenticated_client.get("/statistics/get-statistics/")
    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await StatisticsApiRepo(session).get_general_statistics()

        assert statistics is not None
        assert statistics == {
            "total_users": 2,
            "total_apartments": 1,
            "total_completed_bookings": "Нет данных",
            "total_pending_bookings": 1,
            "total_income": "Нет данных",
        }


async def test_post_submit_general_statistics(
    authenticated_client: AsyncClient, prepare_database
):
    async with async_session_maker() as session:
        booking = Booking(
            id=2,
            user_id=2,
            apartment_id=1,
            start_date=datetime.now(),
            end_date=datetime.now(),
            is_confirmed=False,
            is_completed=False,
            create_at=date(2024, 10, 8),
            update_at=date(2024, 10, 8),
        )
        session.add(booking)
        await session.commit()

    form_data = {
        "start_date": date(2024, 10, 7),
        "end_date": date(2024, 10, 9),
    }

    response = await authenticated_client.post(
        "/statistics/submit-general-statistics/", data=form_data
    )
    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await StatisticsApiRepo(session).get_general_statistics(
            start_date=form_data["start_date"],
            end_date=form_data["end_date"],
        )

        assert statistics is not None
        assert statistics == {
            "total_users": 2,
            "total_apartments": 1,
            "total_completed_bookings": "Нет данных",
            "total_pending_bookings": 1,
            "total_income": "Нет данных",
        }


async def test_post_submit_general_statistics_without_data(
    authenticated_client: AsyncClient, prepare_database
):
    form_data = {
        "start_date": None,
        "end_date": None,
    }
    response = await authenticated_client.post(
        "/statistics/submit-general-statistics/", data=form_data
    )
    assert response.status_code == 200
    async with async_session_maker() as session:
        statistics = await StatisticsApiRepo(session).get_general_statistics(
            start_date=form_data["start_date"],
            end_date=form_data["end_date"],
        )

        assert statistics is not None
        assert statistics == {
            "total_users": 2,
            "total_apartments": 1,
            "total_completed_bookings": "Нет данных",
            "total_pending_bookings": 2,
            "total_income": "Нет данных",
        }


async def test_pending_bookings(authenticated_client: AsyncClient, prepare_database):
    response = await authenticated_client.get("/statistics/pending-bookings")
    assert response.status_code == 200

    async with async_session_maker() as session:

        pending_bookings = await StatisticsApiRepo(session).get_pending_bookings()

        assert pending_bookings is not None

        result = []
        for (
            booking,
            username,
            street,
            house_number,
            apartment_number,
            city_name,
        ) in pending_bookings:
            result.append(
                {
                    "id": booking.id,
                    "username": username,
                    "street": street,
                    "house_number": house_number,
                    "apartment_number": apartment_number,
                    "city_name": city_name,
                }
            )

        assert result == [
            {
                "id": 2,
                "username": "user2",
                "street": "Street",
                "house_number": 1,
                "apartment_number": 1,
                "city_name": "City",
            },
            {
                "id": 1,
                "username": "user1",
                "street": "Street",
                "house_number": 1,
                "apartment_number": 1,
                "city_name": "City",
            },
        ]


async def test_completed_bookings(authenticated_client: AsyncClient, prepare_database):
    async with async_session_maker() as session:
        booking = Booking(
            id=3,
            user_id=2,
            apartment_id=1,
            start_date=date(2024, 10, 8),
            end_date=date(2024, 10, 9),
            is_confirmed=True,
            is_completed=True,
            create_at=date(2024, 10, 8),
            update_at=date(2024, 10, 8),
        )
        session.add(booking)
        await session.commit()

    response = await authenticated_client.get("/statistics/completed-bookings")
    assert response.status_code == 200

    async with async_session_maker() as session:

        completed_bookings = await StatisticsApiRepo(session).get_completed_bookings()

        assert completed_bookings is not None

        result = []
        for (
            booking,
            username,
            street,
            house_number,
            apartment_number,
            city_name,
        ) in completed_bookings:
            result.append(
                {
                    "id": booking.id,
                    "username": username,
                    "street": street,
                    "house_number": house_number,
                    "apartment_number": apartment_number,
                    "city_name": city_name,
                }
            )

        assert result == [
            {
                "id": 3,
                "username": "user2",
                "street": "Street",
                "house_number": 1,
                "apartment_number": 1,
                "city_name": "City",
            }
        ]


async def test_total_income_bookings(
    authenticated_client: AsyncClient, prepare_database
):
    response = await authenticated_client.get("/statistics/total-income-bookings")
    assert response.status_code == 200

    async with async_session_maker() as session:

        total_income = await StatisticsApiRepo(session).get_total_income_bookings()

        assert total_income is not None
        result = []
        for item in total_income:
            result.append(
                {
                    "id": item["booking"].id,
                    "username": item["username"],
                    "street": item["street"],
                    "house_number": item["house_number"],
                    "apartment_number": item["apartment_number"],
                    "city_name": item["city_name"],
                    "income": item["income"],
                    "created_at": item["created_at"],
                }
            )

        assert result == [
            {
                "id": 3,
                "username": "user2",
                "street": "Street",
                "house_number": 1,
                "apartment_number": 1,
                "city_name": "City",
                "income": 1000.0,
                "created_at": datetime(2024, 10, 8, 0, 0),
            }
        ]
