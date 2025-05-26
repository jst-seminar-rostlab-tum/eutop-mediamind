import psycopg2
from psycopg2 import OperationalError
from psycopg2.extensions import connection as PgConnection
from qdrant_client import QdrantClient

from app.core.logger import get_logger

from .config import Configs

logger = get_logger(__name__)


def get_postgresql_connection(cfg: Configs) -> PgConnection:
    if not cfg.DATABASE_URL:
        logger.error("DATABASE_URL not set in config.")
        raise ValueError("DATABASE_URL not set in config.")
    try:
        return psycopg2.connect(dsn=cfg.DATABASE_URL)
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
