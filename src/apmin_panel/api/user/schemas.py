from pydantic import EmailStr
from pydantic import BaseModel
from fastapi import Form


class CreateAdminSchema(BaseModel):
    user_id: int
    email: EmailStr
    password: str

    @classmethod    
    def as_form(
        cls,
        user_id: int = Form(...),
        email: str = Form(...),
        password: str = Form(...),
    ):
        return cls(
            user_id=user_id,
            email=email,
            password=password,
        )