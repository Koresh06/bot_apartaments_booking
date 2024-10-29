from aiogram_dialog import setup_dialogs

from src.tgbot import dp, bot
from src.core.db_helper import async_session_maker
from src.core.config import config
from src.tgbot.dialog import get_all_dialogs, get_routers
from src.tgbot.middlewares.setup import setup_middlewares
from src.tgbot.scheduler_init import scheduler


async def start_bot():

    setup_middlewares(dp=dp, sessionmaker=async_session_maker)

    scheduler.start()

    dp.include_routers(*get_routers())
    dp.include_routers(*get_all_dialogs())
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, config=config)
