import psycopg
from psycopg import OperationalError
from psycopg import connection as PgConnection
from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.core.config import configs
from app.core.logger import get_logger

logger = get_logger(__name__)

engine: AsyncEngine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI))
async_session: AsyncSession = async_sessionmaker(
    engine, expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def get_postgresql_connection() -> PgConnection:
    if not configs.DATABASE_URL:
        logger.error("DATABASE_URL not set in config.")
        raise ValueError("DATABASE_URL not set in config.")
    try:
        return psycopg.connect(dsn=configs.DATABASE_URL)
    except OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
        raise Exception(f"Failed to connect to PostgreSQL database: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL client: {str(e)}")
        raise Exception(f"Failed to initialize PostgreSQL client: {str(e)}")


def get_qdrant_connection() -> QdrantClient:
    if not configs.QDRANT_URL:
        logger.error("QDRANT_URL not set in config.")
        raise ValueError("QDRANT_URL not set in config.")
    try:
        return QdrantClient(
            url=configs.QDRANT_URL, api_key=configs.QDRANT_API_KEY
        )
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {str(e)}")
        raise Exception(f"Failed to initialize Qdrant client: {str(e)}")


"""
 Needed for tests to successfully run. Should no be used.
"""


async def connect() -> None:
    """
    Called on FastAPI startup.
    You can initialize the database here (e.g. run migrations) if you like.
    """
    # If you want to auto-migrate:
    # await init_db()
    pass


async def disconnect() -> None:
    """
    Called on FastAPI shutdown.
    You can cleanly dispose your engine here.
    """
    # If you want to fully dispose:
    # engine.sync_engine.dispose()
    pass
