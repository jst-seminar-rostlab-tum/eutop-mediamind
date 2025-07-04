import json
import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy.future import select

from app.core.db import engine
from app.core.logger import get_logger
from app.models import Subscription
from app.services.seeding_service.seeding_credentials import (
    seed_credentials_from_env,
    seed_credentials_from_file,
)

logger = get_logger(__name__)


def load_json_data(file_path: str) -> list[dict]:
    """Utility to load JSON seed data"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_data():
    async with engine.begin() as conn:
        async with AsyncSession(bind=conn) as session:
            await seed_subscriptions(session)

    # Seed credentials after subscriptions are created
    await seed_credentials_from_env()

    # For local development, try to load from a local credentials file
    local_credentials_path = "./data/newspapers_accounts.json"
    if os.path.exists(local_credentials_path):
        await seed_credentials_from_file(local_credentials_path)


async def seed_subscriptions(session: AsyncSession) -> None:
    """
    Seed initial subscriptions data if table is empty
    or update existing ones by name
    """

    # Load seed data from JSON file
    seed_file_path = os.path.abspath("./data/subscriptions.json")
    seed_data = load_json_data(seed_file_path)

    for item in seed_data:
        # Try to find existing subscription by name
        result = await session.execute(
            select(Subscription).where(Subscription.name == item["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing fields
            for key, value in item.items():
                setattr(existing, key, value)
            session.add(existing)
        else:
            # Insert new subscription
            subscription = Subscription(**item)
            session.add(subscription)

    await session.commit()
    logger.info("Subscriptions data seeded/updated successfully.")
