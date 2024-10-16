from jose import jwt
from datetime import datetime, timedelta, timezone

from src.core.config import config

ALGORITHM = "HS256"
access_token_jwt_subject = "access"


def create_token(user_id: int):
    access_token_expires = timedelta(minutes=config.api.access_token_expire_minutes)
    return {
        "access_token": create_access_token(
            data={"user_id": user_id}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """Создание токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode, config.api.secret_key, algorithm=ALGORITHM)
    return encoded_jwt