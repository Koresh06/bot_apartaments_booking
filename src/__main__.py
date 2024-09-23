import asyncio
import logging
from aiogram_dialog import setup_dialogs
import uvicorn

from src.tgbot.bot import dp, bot
from src.core.config import settings
from src.tgbot.middlewares.db_session import DbSessionMiddleware
from src.core.db_helper import db_helper

from src.tgbot.dialog import start_dialog, register_landlord_dialog, main_manu_dialog


logger = logging.getLogger(__name__)

dp.update.middleware(DbSessionMiddleware(sessionmaker=db_helper.sessionmaker))

dp.include_routers(
    register_landlord_dialog,
    main_manu_dialog,
    start_dialog,
)
setup_dialogs(dp)


async def start_bot():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
               "[%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    asyncio.create_task(start_bot())

    config = uvicorn.Config(
        "src.run_fastapi:app", 
        host=settings.api.host,
        port=settings.api.port,
        log_level="info",
        reload=True,
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as exxit:
        logger.info(f"Бот закрыт: {exxit}")