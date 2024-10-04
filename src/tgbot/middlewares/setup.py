import sqlalchemy.orm
from aiogram import Dispatcher

from .db_session import DbSessionMiddleware
from .scheduler import SchedulerMiddleware
from src.tgbot.scheduler_init import scheduler


def setup_middlewares(
    dp: Dispatcher,
    sessionmaker: sqlalchemy.orm.sessionmaker,
):
    dp.update.middleware(DbSessionMiddleware(sessionmaker=sessionmaker))
    dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))