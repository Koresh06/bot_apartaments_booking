import sqlalchemy.orm
from aiogram import Dispatcher

from .banned_user import BanCheckMiddleware
from .scheduler import SchedulerMiddleware
from .db_session import DbSessionMiddleware
from src.tgbot.scheduler_init import scheduler


def setup_middlewares(
    dp: Dispatcher,
    sessionmaker: sqlalchemy.orm.sessionmaker,
):
    dp.update.outer_middleware(DbSessionMiddleware(sessionmaker=sessionmaker))
    dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))
    dp.message.middleware(BanCheckMiddleware(sessionmaker=sessionmaker))