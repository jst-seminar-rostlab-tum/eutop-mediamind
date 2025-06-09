import json
import os

from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Session, SQLModel
from sqlalchemy import create_engine

from app.core.config import configs
from app.core.logger import get_logger

from .config import Configs

logger = get_logger(__name__)

engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI))

sync_engine = create_engine(
    str(configs.SQLALCHEMY_DATABASE_URI))

async_session = async_sessionmaker(engine, expire_on_commit=False)


def load_json_data(file_path: str) -> list[dict]:
    """Utility to load JSON seed data"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def init_db(session: Session):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        seed_subscriptions(session)


def seed_subscriptions(session: Session) -> None:
    """Seed initial subscriptions data if table is empty"""
    from app.models.subscription import Subscription

    # Check if table is empty
    if session.query(Subscription).first():
        logger.info("Subscriptions table already seeded. Skipping seeding.")
        return

    # Load seed data from JSON file
    seed_file_path = os.path.abspath("./data/subscriptions.json")
    seed_data = load_json_data(seed_file_path)

    for item in seed_data:
        subscription = Subscription(**item)
        session.add(subscription)

    session.commit()
    logger.info("Initial subscriptions data seeded successfully.")


def get_qdrant_connection(cfg: Configs) -> QdrantClient:
    if not cfg.QDRANT_URL:
        logger.error("QDRANT_URL not set in config.")
        raise ValueError("QDRANT_URL not set in config.")
    try:
        return QdrantClient(url=cfg.QDRANT_URL)
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant client: {str(e)}")
        raise Exception(f"Failed to initialize Qdrant client: {str(e)}")
