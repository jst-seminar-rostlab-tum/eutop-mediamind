import json
import os
from typing import Any, Dict

from sqlalchemy.future import select

from app.core.config import configs
from app.core.db import async_session
from app.core.logger import get_logger
from app.models.subscription import Subscription

logger = get_logger(__name__)


async def seed_credentials_from_json(credentials_data: Dict[str, Any]) -> None:
    """
    Seed subscription credentials from a json.

    Args:
        credentials_data: Dictionary with subscription names as keys and
                          credential objects as values containing user_email
                          and password
    """
    async with async_session() as session:
        for subscription_name, credentials in credentials_data.items():
            # Find the subscription by name
            result = await session.execute(
                select(Subscription).where(
                    Subscription.name == subscription_name
                )
            )
            subscription = result.scalar_one_or_none()

            if subscription:
                # Store credentials as encrypted JSON
                subscription.secrets = json.dumps(credentials)
                session.add(subscription)
                logger.info(
                    f"Updated credentials for subscription: "
                    f"{subscription_name}"
                )
            else:
                logger.warning(f"Subscription not found: {subscription_name}")

        await session.commit()
        logger.info("Credentials seeding completed")


async def seed_credentials_from_file(file_path: str) -> None:
    """
    Seed subscription credentials from a JSON file.

    Args:
        file_path: Path to the JSON file containing credentials
    """
    if not os.path.exists(file_path):
        logger.info(f"Credentials file not found: {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        credentials_data = data.get("CREDENTIALS", {})
        if credentials_data:
            await seed_credentials_from_json(credentials_data)
        else:
            logger.warning("No CREDENTIALS section found in the file")

    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        logger.error(f"Failed to load credentials from file {file_path}: {e}")


async def seed_credentials_from_env() -> None:
    """
    Seed subscription credentials.
    This is used in production deployments.
    """
    subscription_accounts = configs.SUBSCRIPTION_ACCOUNTS
    if not subscription_accounts:
        logger.info("No SUBSCRIPTION_ACCOUNTS environment variable found")
        return

    try:
        credentials_data = subscription_accounts.get("CREDENTIALS", {})
        if credentials_data:
            await seed_credentials_from_json(credentials_data)
        else:
            logger.info(
                "No CREDENTIALS section found in SUBSCRIPTION_ACCOUNTS"
            )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse SUBSCRIPTION_ACCOUNTS: {e}")
