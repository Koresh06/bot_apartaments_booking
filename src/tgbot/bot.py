from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import SimpleEventIsolation
from redis.asyncio import Redis
from src.core.config import settings


bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

redis = Redis(
    host=settings.redis.host,  
    port=settings.redis.port,       
    db=settings.redis.db,             
)

storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))

dp = Dispatcher()



