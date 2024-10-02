from fastapi import Form
from pydantic import BaseModel


class LoginData(BaseModel):
    username: str
    password: str 

    @classmethod
    async def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
    ) -> "LoginData":
        return cls(
            username=username,
            password=password
        )