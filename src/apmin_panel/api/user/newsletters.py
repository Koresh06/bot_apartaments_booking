from src.tgbot.bot import bot
from src.core.config import config


async def send_newsletter_notification(tg_ids: list, message: str) -> None:
    for id in tg_ids:
        await bot.send_message(
            chat_id=id,
            text=message
        )

    await bot.send_message(chat_id=config.tg_bot.admin_id, text="Рассылка завершена успешно")
    