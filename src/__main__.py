import asyncio
import logging
import uvicorn
from aiogram_dialog import setup_dialogs

from src.tgbot.bot import dp, bot
from src.core.config import settings
from src.tgbot.middlewares.setup import setup_middlewares
from src.core.db_helper import db_helper
from src.tgbot.scheduler_init import scheduler

from src.tgbot.dialog import get_routers


logger = logging.getLogger(__name__)



async def start_bot():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
               "[%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    scheduler.start()

    setup_middlewares(dp=dp, sessionmaker=db_helper.sessionmaker)

    dp.include_routers(*get_routers())
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():

    # Запуск бота в фоне
    asyncio.create_task(start_bot())

    # Запуск FastAPI приложения
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