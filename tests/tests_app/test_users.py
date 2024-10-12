from datetime import datetime
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from src.apmin_panel.api.auth_helpers import create_hashed_cookie
from src.apmin_panel.api.services.users_api_service import UsersApiRepo


BASE_PATH_AUTH = "src.apmin_panel.api"
BASE_PATH_SERVICE = "src.apmin_panel.api.services.users_api_service"


def test_admin_auth(mocker):
    hashed_token = create_hashed_cookie("admin_login", "your_secret_key")
    mocker.patch(f"{BASE_PATH_AUTH}.auth_helpers.create_hashed_cookie", return_value=hashed_token)


async def test_get_users(authenticated_client: AsyncClient, mocker):
    test_admin_auth(mocker)

    mock_get_all_users = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.get_all_users", new_callable=AsyncMock)
    mock_get_all_users.return_value = [
        {
            "id": 1,
            "tg_id": 123456789,
            "chat_id": 987654321,
            "username": "user1",
            "full_name": "User One",
            "is_admin": False,
            "is_banned": False,
            "create_at": datetime(2024, 1, 1, 12, 0),
            "update_at": datetime(2024, 1, 1, 12, 0),
        },
        {
            "id": 2,
            "tg_id": 223456789,
            "chat_id": 887654321,
            "username": "user2",
            "full_name": "User Two",
            "is_admin": False,
            "is_banned": False,
            "create_at": datetime(2024, 1, 2, 12, 0),
            "update_at": datetime(2024, 1, 2, 12, 0),
        }
    ]

    response = await authenticated_client.get("/users/get-users/")

    assert response.status_code == 200

    mock_get_all_users.assert_awaited_once()


async def test_get_users_invalid_cookie(authenticated_client: AsyncClient, mocker):
    response = await authenticated_client.get("/users/get-users/")

    assert response.status_code == 302
    assert "Location" in response.headers 
    assert response.headers["Location"] == "/auth/login" 

    mock_get_all_users = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.get_all_users", new_callable=AsyncMock)
    mock_get_all_users.assert_not_awaited()


async def test_get_user_detail(authenticated_client: AsyncClient, mocker):
    hashed_token = create_hashed_cookie("admin_login", "your_secret_key")
    mocker.patch(f"{BASE_PATH_AUTH}.auth_helpers.create_hashed_cookie", return_value=hashed_token)

    user_id = 1
    mock_user_detail = {
        "id": user_id,
        "tg_id": 123456789,
        "chat_id": 987654321,
        "username": "user1",
        "full_name": "User One",
        "is_admin": False,
        "is_banned": False,
        "create_at": datetime(2024, 1, 1, 12, 0),
        "update_at": datetime(2024, 1, 1, 12, 0),
    }
    
    mock_get_user_by_id = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.get_user_by_id", new_callable=AsyncMock)
    mock_get_user_by_id.return_value = mock_user_detail

    response = await authenticated_client.get(f"/users/get-user-detail/{user_id}")

    assert response.status_code == 200

    mock_get_user_by_id.assert_awaited_once_with(user_id)


async def test_banned_user(authenticated_client: AsyncClient, mocker):
    test_admin_auth(mocker)

    user_id = 1
    mock_user_detail = {
        "id": user_id,
        "tg_id": 123456789,
        "chat_id": 987654321,
        "username": "user1",
        "full_name": "User One",
        "is_admin": False,
        "is_banned": False,
        "create_at": datetime(2024, 1, 1, 12, 0),
        "update_at": datetime(2024, 1, 1, 12, 0),
    }
    
    mock_banned_user = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.banned_user_by_id", new_callable=AsyncMock)
    mock_get_user_by_id = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.get_user_by_id", new_callable=AsyncMock)
    
    mock_banned_user.return_value = True 
    mock_get_user_by_id.return_value = mock_user_detail

    response = await authenticated_client.post(f"/users/{user_id}/banned")

    assert response.status_code == 200

    mock_banned_user.assert_awaited_once_with(user_id)
    mock_get_user_by_id.assert_awaited_once_with(user_id)



async def test_unbanned_user(authenticated_client: AsyncClient, mocker):
    test_admin_auth(mocker)

    user_id = 1
    mock_user_detail = {
        "id": user_id,
        "tg_id": 123456789,
        "chat_id": 987654321,
        "username": "user1",
        "full_name": "User One",
        "is_admin": False,
        "is_banned": False,
        "create_at": datetime(2024, 1, 1, 12, 0),
        "update_at": datetime(2024, 1, 1, 12, 0),
    }
    
    mock_unbanned_user = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.unbanned_user_by_id", new_callable=AsyncMock)
    mock_get_user_by_id = mocker.patch(f"{BASE_PATH_SERVICE}.UsersApiRepo.get_user_by_id", new_callable=AsyncMock)
    
    mock_unbanned_user.return_value = True 
    mock_get_user_by_id.return_value = mock_user_detail

    response = await authenticated_client.post(f"/users/{user_id}/unbanned")

    assert response.status_code == 200

    mock_unbanned_user.assert_awaited_once_with(user_id)
    mock_get_user_by_id.assert_awaited_once_with(user_id)



