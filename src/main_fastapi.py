# main_fastapi.py

import asyncio
import logging
from src.run_fastapi import start_app
from .setup_logging import setup_main_logging


logger = logging.getLogger(__name__)


async def main():
    setup_main_logging()
    await start_app()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("FastAPI app has been stopped")
