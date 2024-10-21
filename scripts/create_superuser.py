import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from src.core.db_helper import async_session_maker
from src.apmin_panel.api.auth.service import AuthApiRepo


async def create_superuser() -> None:
    async with async_session_maker() as session:  
        print("Создание суперпользователя")
        tg_id = int(input("Укажите TG_ID пользователя: "))
        email = input("Укажите email пользователя: ")
        password = input("Укажите пароль пользователя: ")

        # Проверяем, существует ли пользователь
        super_user = await AuthApiRepo(session).get_by_tg_id(tg_id)
        if not super_user:
            print("Пользователь с таким TG_ID не существует")
        elif super_user.is_superuser:
            print("Пользователь уже является суперпользователем")
        else:
            # Создаем суперпользователя
            await AuthApiRepo(session).create_superuser(
                tg_id=tg_id,
                email=email,
                password=password
            )
            print("Суперпользователь создан")


if __name__ == '__main__':
    asyncio.run(create_superuser())
