import asyncio
import logging
from aiogram_dialog import setup_dialogs
import uvicorn

from src.tgbot.bot import dp, bot
from src.core.config import settings
from src.tgbot.dialog.bg_manager_factory import MyBgManagerFactory
from src.tgbot.middlewares.db_session import DbSessionMiddleware
from src.core.db_helper import db_helper

from src.tgbot.dialog import (
    register_landlord_dialog, 
    menu_loandlord_dialog,
    register_apartament_dialog,
    my_apartmernt_landlord_dialog,
    edit_apartment_dialog,
    filter_catalog_apartments_dialog,
    city_filter_apartment_dialog,
    catalog_users_apartments_dialog,
    price_range_filter_dialog,
    rooms_filter_dialog,
    booking_apartment,
    confirm_booking_landlord_dialog,
    register_name_city_dialog,
    main_admin_dialog
)


logger = logging.getLogger(__name__)

bg_manager = MyBgManagerFactory()

dp.update.middleware(DbSessionMiddleware(
    sessionmaker=db_helper.sessionmaker,
    bg_manager=bg_manager,
    bot=bot  
))

dp.include_routers(
    register_name_city_dialog,
    # confirm_booking_landlord_dialog,
    main_admin_dialog,
    booking_apartment,
    rooms_filter_dialog,
    price_range_filter_dialog,
    catalog_users_apartments_dialog,
    filter_catalog_apartments_dialog,
    city_filter_apartment_dialog,
    edit_apartment_dialog,
    my_apartmernt_landlord_dialog,
    register_apartament_dialog,
    menu_loandlord_dialog,
    register_landlord_dialog,
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