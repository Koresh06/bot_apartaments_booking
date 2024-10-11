from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import BaseMiddleware


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        super().__init__()
        self._scheduler = scheduler

    async def __call__(self,handler,event,data):
        data["scheduler"] = self._scheduler
        return await handler(event, data)