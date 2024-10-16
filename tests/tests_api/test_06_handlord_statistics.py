from datetime import date
from httpx import AsyncClient

from src.apmin_panel.api.landlord.service import LandlordApiRepo
from ..conftest import async_session_maker


async def test_statistics_landlord_by_id(
    authenticated_client: AsyncClient,
    prepare_database,
):
    landlord_id = 1
    response = await authenticated_client.get(f"/landlord/statistics/{landlord_id}")

    assert response.status_code == 200

    async with async_session_maker() as session:
        landlord_statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(landlord_id=landlord_id)

        assert landlord_statistics["total_apartments"]  == 1
        assert landlord_statistics["total_completed_bookings"] == 1
        assert landlord_statistics["total_pending_bookings"] == 2
        assert landlord_statistics["total_income"] == 1000.0


async def test_post_submit_landlord_statistics(
    authenticated_client: AsyncClient,
    prepare_database,
):
    form_data = {
        "landlord_id": 1,
        "start_date": date(2024, 10, 7),
        "end_date": date(2024, 10, 9),
    }

    response = await authenticated_client.post("/landlord/submit-landlord-statistics/", data=form_data)

    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(
            landlord_id=form_data["landlord_id"],
            start_date=form_data["start_date"],
            end_date=form_data["end_date"],
        )

        assert statistics is not None
        assert statistics["total_apartments"] == 1
        assert statistics["total_completed_bookings"] == 1
        assert statistics["total_pending_bookings"] == 1
        assert statistics["total_income"] == 1000.0


async def test_post_submit_landlord_statistics_without_data(
    authenticated_client: AsyncClient,
    prepare_database,
):
    form_data = {
        "landlord_id": 1,
        "start_date": None,
        "end_date": None,
    }

    response = await authenticated_client.post("/landlord/submit-landlord-statistics/", data=form_data)

    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(
            landlord_id=form_data["landlord_id"],
            start_date=form_data["start_date"],
            end_date=form_data["end_date"],
        )

        assert statistics is not None
        assert statistics["total_apartments"] == 1
        assert statistics["total_completed_bookings"] == 1
        assert statistics["total_pending_bookings"] == 2
        assert statistics["total_income"] == 1000.0


async def test_get_complete_bookings(
    authenticated_client: AsyncClient, 
    prepare_database
):
    landlord_id = 1

    response = await authenticated_client.get(f"/landlord/{landlord_id}/completed-bookings")
    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await LandlordApiRepo(session).get_completed_bookings_by_landlord_id(landlord_id=landlord_id)

        assert statistics is not None
        assert statistics[0][0].id == 3
        assert statistics[0][1] == "user2"
        assert statistics[0][2] == "Street"
        assert statistics[0][3] == 1
        assert statistics[0][4] == 1
        assert statistics[0][5] == "City"


async def test_get_pending_bookings(
    authenticated_client: AsyncClient, 
    prepare_database
):
    landlord_id = 1

    response = await authenticated_client.get(f"/landlord/{landlord_id}/pending-bookings")
    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await LandlordApiRepo(session).get_pending_bookings_by_landlord_id(landlord_id=landlord_id)

        assert statistics is not None
        assert statistics[0][0].id == 2
        assert statistics[0][1] == "user2"
        assert statistics[0][2] == "Street"
        assert statistics[0][3] == 1
        assert statistics[0][4] == 1
        assert statistics[0][5] == "City"


async def test_get_total_income_bookings(
    authenticated_client: AsyncClient, 
    prepare_database
):
    landlord_id = 1

    response = await authenticated_client.get(f"/landlord/{landlord_id}/total-income-bookings")
    assert response.status_code == 200

    async with async_session_maker() as session:
        statistics = await LandlordApiRepo(session).get_total_income_bookings_by_landlord_id(landlord_id=landlord_id)

        assert statistics[0]["booking"].id == 3
        assert statistics[0]["username"] == "user2"
        assert statistics[0]["street"] == "Street"
        assert statistics[0]["house_number"] == 1
        assert statistics[0]["apartment_number"] == 1
        assert statistics[0]["city_name"] == "City"
        assert statistics[0]["income"] == 1000.0