from typing import Optional
from fastapi import Request
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """ Схема для токена
    """
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """ Схема для
    """
    user_id: int = None


class UserCreateInRegistration(BaseModel):
    """ Свойства для получения через API при регистрации
    """
    user_id: int
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")