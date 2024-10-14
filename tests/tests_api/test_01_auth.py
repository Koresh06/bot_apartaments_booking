import pytest
from bs4 import BeautifulSoup
from fastapi import status
from httpx import AsyncClient

from src.core.config import config


async def test_login_form_renders_template(async_client: AsyncClient):
    response = await async_client.get("/auth/login")

    assert response.status_code == status.HTTP_200_OK


async def test_login_success(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/login",
        data={"username": config.api.admin_login, "password": config.api.admin_password},
    )

    assert response.status_code == 302
    assert response.cookies["admin_token"] 


async def test_login_failure(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/login",
        data={"username": "", "password": "wrong_password"}
    )

    assert response.status_code == 200  
    assert "Неверное имя пользователя или пароль" in response.text 


async def test_login_unknown_error(async_client: AsyncClient):
    response = await async_client.post(
        "/auth/login",
        data={"username": "username", "password": "password"} 
    )

    assert response.status_code == 200
    
    soup = BeautifulSoup(response.text, "html.parser")
    error_message = soup.find("div", class_="alert alert-danger") 

    assert error_message is not None
    assert "Неверное имя пользователя или пароль" in error_message.text.strip()


async def test_logout(async_client: AsyncClient):
    response = await async_client.get("/auth/logout")

    assert response.status_code == 200

    assert "Успешный выход из системы" in response.text

    cookies = response.cookies
    assert "admin_token" not in cookies