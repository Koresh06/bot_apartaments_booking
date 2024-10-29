from datetime import datetime
from unittest.mock import Mock

from aiogram import Dispatcher
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Update, Chat, User, Message
from aiogram.filters import CommandStart

from aiogram_dialog import DialogManager, setup_dialogs
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.test_tools import BotClient, MockMessageManager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from src.core.models.users import Users
from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog import get_all_dialogs
from src.tgbot.middlewares.db_session import DbSessionMiddleware

from .mocked_aiogram import MockedBot, MockedSession
from src.tgbot.services.users_bot_service import BotUserRepo
from src.tgbot.dialog.apartments_users.apartments_filters_catalog import command_start_process
from src.tgbot.dialog.apartments_users.apartments_filters_catalog import router as filter_catalog_apartments_dialog


def make_message(user_id: int, text: str) -> Message:
    user = User(
        id=user_id,
        username="user",
        first_name="User",
        last_name="User",
        full_name="User User",
        is_bot=False,
    )
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    return Message(
        message_id=1,
        from_user=user,
        chat=chat,
        date=datetime.now(),
        text=text,
    )


async def test_cmd_start(dp: Dispatcher, session: AsyncSession, mock_manager: DialogManager):
    dp.message.register(command_start_process, CommandStart)

    client = BotClient(dp=dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # command_start_process
    user_id = 123456
    message: Message = make_message(user_id, "/start")
    await client.send("/start")

    repo: RequestsRepo = mock_manager.middleware_data.get("repo")
    await repo.bot_users.add_user(
        tg_id=user_id,
        chat_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        full_name=message.from_user.full_name,
    )






    # user_id = 123456
    # message: Message = make_message(user_id, "/start")
    # bot.add_result_for(SendMessage, ok=True)
    # await dp.feed_update(bot, Update(message=message, update_id=1))

    # user_response: Users = await BotUserRepo(session).add_user(
    #     tg_id=user_id,
    #     chat_id=user_id,
    #     username=message.from_user.username,
    #     first_name=message.from_user.first_name,
    #     last_name=message.from_user.last_name,
    #     full_name=message.from_user.full_name,
    # )
    # assert user_response is not None
    # assert user_response.tg_id == user_id
