import psycopg
from psycopg import OperationalError
from psycopg import connection as PgConnection
from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Session, SQLModel

from app.core.config import configs
from app.core.logger import get_logger

from .config import Configs

logger = get_logger(__name__)

engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI))

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db(session: Session):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def get_postgresql_connection(cfg: Configs) -> PgConnection:
    if not cfg.DATABASE_URL:
        logger.error("DATABASE_URL not set in config.")
        raise ValueError("DATABASE_URL not set in config.")
    try:
        return psycopg.connect(dsn=cfg.DATABASE_URL)
    except OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
        raise Exception(f"Failed to connect to PostgreSQL database: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL client: {str(e)}")
        raise Exception(f"Failed to initialize PostgreSQL client: {str(e)}")


def get_qdrant_connection(cfg: Configs) -> QdrantClient:
    if not cfg.QDRANT_URL:
        logger.error("QDRANT_URL not set in config.")
        raise ValueError("QDRANT_URL not set in config.")
    try:
        return QdrantClient(url=cfg.QDRANT_URL)
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {str(e)}")
        raise Exception(f"Failed to initialize Qdrant client: {str(e)}")
