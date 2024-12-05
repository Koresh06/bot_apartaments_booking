# main_bot.py

import logging
import asyncio

from src.tgbot.bot import start_bot
from .setup_logging import setup_main_logging

logger = logging.getLogger(__name__)


async def main():
    setup_main_logging()
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot has been stopped")
