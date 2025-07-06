import psycopg
import redis
from psycopg import OperationalError
from psycopg import connection as PgConnection
from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import configs
from app.core.logger import get_logger

logger = get_logger(__name__)

engine: AsyncEngine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI))
async_session: AsyncSession = async_sessionmaker(
    engine, expire_on_commit=False
)

redis_engine = redis.Redis(
    host=configs.REDIS_HOST,
    port=configs.REDIS_PORT,
    db=configs.REDIS_DB,
    password=getattr(configs, "REDIS_PASSWORD", None),
)


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
    """
    Initializes and returns a Qdrant client.

    Raises:
        ValueError: If QDRANT_URL is not set in the configuration.
        RuntimeError: If the client initialization fails.
    """

    try:
        if configs.ENVIRONMENT == "local":
            client = QdrantClient(host="localhost", port=6333)
        else:
            client = QdrantClient(
                url=configs.QDRANT_URL,
                api_key=configs.QDRANT_API_KEY,
            )
        return client

    except Exception as err:
        msg = f"Failed to initialize Qdrant client: {err}"
        logger.error(msg)
        raise RuntimeError(msg) from err

def get_redis_url() -> str:
    """
    Constructs a Redis URL from the connection pool parameters.
    """
    from urllib.parse import quote

    host = redis_engine.connection_pool.connection_kwargs.get("host")
    port = redis_engine.connection_pool.connection_kwargs.get("port")
    db = redis_engine.connection_pool.connection_kwargs.get("db")
    username = redis_engine.connection_pool.connection_kwargs.get("username")
    password = redis_engine.connection_pool.connection_kwargs.get("password")

    if username and password:
        url = f"redis://{quote(username)}:{quote(password)}@{host}:{port}/{db}"
    elif password:
        url = f"redis://:{quote(password)}@{host}:{port}/{db}"
    else:
        url = f"redis://{host}:{port}/{db}"

    return url
