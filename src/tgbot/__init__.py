from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder

from src.core.config import config


bot: Bot = Bot(
    token=config.tg_bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

storage = RedisStorage.from_url(
    config.redis.dsn(),
    key_builder=DefaultKeyBuilder(with_destiny=True, with_bot_id=True),
)

dp: Dispatcher = Dispatcher()