import asyncio

from app.core.db import init_db
from app.core.logger import get_logger
from app.core.config import configs

logger = get_logger(__name__)

async def init() -> None:
    await init_db()

async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
