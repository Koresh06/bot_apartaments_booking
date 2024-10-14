from datetime import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.apmin_panel.api.services.users_api_service import UsersApiRepo
from src.core.models import Users
from ..conftest import async_session_maker


async def test_not_authenticated_client(async_client: AsyncClient, prepare_database):
    response = await async_client.get("/users/get-users/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"


async def test_get_users(authenticated_client: AsyncClient, prepare_database): 
    async with async_session_maker() as session:
        user1 = Users(
            id=1,
            tg_id=123456789,
            chat_id=987654321,
            username="user1",
            full_name="User One",
            is_admin=False,
            is_banned=False,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        user2 = Users(
            id=2,
            tg_id=987654321,
            chat_id=123456789,
            username="user2",
            full_name="User Two",
            is_admin=False,
            is_banned=False,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        session.add(user1)
        session.add(user2)
        await session.commit()
        await session.refresh(user2)


        user_from_db = await UsersApiRepo(session).get_all_users()

        assert user_from_db[1].id == user1.id
        assert user_from_db[1].tg_id == user1.tg_id
        assert user_from_db[1].chat_id == user1.chat_id
        assert user_from_db[1].username == user1.username
        assert user_from_db[1].full_name == user1.full_name
        assert user_from_db[1].is_admin == user1.is_admin
        assert user_from_db[1].is_banned == user1.is_banned
        assert user_from_db[1].create_at == user1.create_at
        assert user_from_db[1].update_at == user1.update_at
            

    response = await authenticated_client.get("/users/get-users/")
    assert response.status_code == 200


async def test_get_user_detail(authenticated_client: AsyncClient, prepare_database): 
    user_id = 1
    response = await authenticated_client.get(f"/users/get-user-detail/{user_id}",)

    assert response.status_code == 200

    async with async_session_maker() as session:
        user_from_db = await UsersApiRepo(session).get_user_by_id(user_id)

    assert user_from_db.id == user_id 
    assert user_from_db.username == "user1"


async def test_banned_user(authenticated_client: AsyncClient, prepare_database): 
    user_id = 1
    response = await authenticated_client.post(f"/users/{user_id}/banned",)

    assert response.status_code == 200

    async with async_session_maker() as session:
        user_from_db = await UsersApiRepo(session).get_user_by_id(user_id)

    assert user_from_db.id == user_id 
    assert user_from_db.is_banned == True


async def test_unbanned_user(authenticated_client: AsyncClient, prepare_database):
    user_id = 1
    response = await authenticated_client.post(f"/users/{user_id}/unbanned",)

    assert response.status_code == 200

    async with async_session_maker() as session:
        user_from_db = await UsersApiRepo(session).get_user_by_id(user_id)

    assert user_from_db.id == user_id 
    assert user_from_db.is_banned == False




