from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import select, delete

from src.apmin_panel.api.services.landlord_api_service import LandlordApiRepo
from src.core.models import Landlords
from ..conftest import async_session_maker


async def test_get_landlords(authenticated_client: AsyncClient, prepare_database):
    async with async_session_maker() as session:
        landlord1 = Landlords(
            id=1,
            user_id=1,
            company_name="Name1",
            phone="1234567890",
            create_at=datetime.now(),
            update_at=datetime.now(),
        )

        session.add(landlord1)
        await session.commit()
        await session.refresh(landlord1)

        landlord_from_db: Landlords = await LandlordApiRepo(session).get_all_landlords()

        assert landlord_from_db[0].id == landlord1.id
        assert landlord_from_db[0].user_id == landlord1.user_id
        assert landlord_from_db[0].company_name == landlord1.company_name
        assert landlord_from_db is not None
        assert landlord_from_db[0].phone == landlord1.phone
        assert landlord_from_db[0].create_at == landlord1.create_at
        assert landlord_from_db[0].update_at == landlord1.update_at

    response = await authenticated_client.get("/landlord/get-landlords")
    assert response.status_code == 200


async def test_get_create_landlord(authenticated_client: AsyncClient, prepare_database):
    response = await authenticated_client.get("/landlord/create-landlord")
    assert response.status_code == 200

    async with async_session_maker() as session:
        username_users = await LandlordApiRepo(session).get_users_not_landlord()

        assert username_users[0].username == "user2"


async def test_post_create_landlord(
    authenticated_client: AsyncClient, prepare_database
):
    async with async_session_maker() as session:
        await session.execute(delete(Landlords))
        await session.commit()

    form_data = {
        "user_id": 1, 
        "company_name": "Test Company",
        "phone": "1234567890",
    }

    response = await authenticated_client.post("/landlord/submit-create-landlord", data=form_data)

    assert response.status_code == 303

    async with async_session_maker() as session:
        landlord = await session.execute(select(Landlords).where(Landlords.user_id == 1))
        assert landlord.scalars().first() is not None


