import json
import os

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
from sqlalchemy.future import select
from sqlmodel import SQLModel

from app.core.config import configs
from app.core.logger import get_logger
from app.models import Subscription

logger = get_logger(__name__)

engine: AsyncEngine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI))
async_session: AsyncSession = async_sessionmaker(
    engine, expire_on_commit=False
)


def load_json_data(file_path: str) -> list[dict]:
    """Utility to load JSON seed data"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        async with AsyncSession(bind=conn) as session:
            await seed_subscriptions(session)


async def seed_subscriptions(session: AsyncSession) -> None:
    """Seed initial subscriptions data if table is empty"""

    # Check if table is empty
    result = await session.execute(select(Subscription).limit(1))
    if result.scalars().first():
        logger.info("Subscriptions table already seeded. Skipping seeding.")
        return

    # Load seed data from JSON file
    seed_file_path = os.path.abspath("./data/subscriptions.json")
    seed_data = load_json_data(seed_file_path)

    for item in seed_data:
        subscription = Subscription(**item)
        session.add(subscription)

    await session.commit()
    logger.info("Initial subscriptions data seeded successfully.")


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
