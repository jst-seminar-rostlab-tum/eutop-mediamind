from typing import Any, Dict, List, Optional, Union

from app.core.db import async_session
from app.repositories.user_repository import create_user as repo_create_user
from app.repositories.user_repository import (
    get_user_by_clerk_id as repo_get_by_clerk_id,
)
from app.repositories.user_repository import get_user_list_from_organization
from app.repositories.user_repository import update_user as repo_update_user
from app.schemas.user_schema import UserEntity


class UserService:
    @staticmethod
    async def list_users(
        user: UserEntity,
    ) -> Union[List[UserEntity], UserEntity]:
        """
        Return all users in the same organization, or self if no org.
        Superusers receive all users.
        """
        async with async_session() as session:
            return await get_user_list_from_organization(user, session)

    @staticmethod
    async def get_by_clerk_id(
        clerk_id: str,
    ) -> Optional[UserEntity]:
        """
        Fetch a user by Clerk ID, return UserEntity or None.
        """
        async with async_session() as session:
            return await repo_get_by_clerk_id(
                clerk_id=clerk_id, session=session
            )

    @staticmethod
    async def create_user_from_clerk(
        clerk_id: str,
        email: Optional[str],
        data: Dict[str, Any],
    ) -> UserEntity:
        """
        Create a new local User model from Clerk data.
        """
        async with async_session() as session:
            return await repo_create_user(session, clerk_id, email, data)

    @staticmethod
    async def sync_user_fields(
        existing: UserEntity,
        email: Optional[str],
        data: Dict[str, Any],
    ) -> UserEntity | None:
        """
        Update local User fields if they differ from Clerk data.
        """
        async with async_session() as session:
            return await repo_update_user(session, existing, email, data)
