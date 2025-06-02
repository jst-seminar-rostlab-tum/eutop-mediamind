import os
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extensions import connection as PgConnection
from qdrant_client import QdrantClient
from sqlmodel import Session, SQLModel, create_engine

import json
from app.core.config import configs
from app.core.logger import get_logger

from .config import Configs

logger = get_logger(__name__)

engine = create_engine(str(configs.SQLALCHEMY_DATABASE_URI))


def load_json_data(file_path: str) -> list[dict]:
    """Utility to load JSON seed data"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)
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
