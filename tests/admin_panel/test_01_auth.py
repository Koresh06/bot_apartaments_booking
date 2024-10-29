from bs4 import BeautifulSoup
from fastapi import status
from httpx import AsyncClient

from src.core.config import config
from src.run_fastapi import app


async def test_create_admin(prepare_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/users/submit-create-admin",
            data={
                "user_id": 1,
                "email": "test@example.com",
                "password": "test_password",
            },
        )
    assert response.status_code == 200


async def test_access_token_success(prepare_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/access-token",
            data={
                "user_id": 1,
                "username": "test@example.com",
                "password": "test_password",
            },
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
