from typing import Any, Dict, List, Optional

from app.core.db import async_session
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserEntity


class UserService:
    @staticmethod
    async def get_all_by_organization(
        user: UserEntity,
    ) -> List[User]:
        """
        Return all users in the same organization, or self if no org.
        Superusers receive all users.
        """
        if (not user.is_superuser) & (user.organization_id is None):
            return [user]
        async with async_session() as session:
            return await UserRepository.get_users_by_organization(
                user.organization_id, session
            )

    @staticmethod
    async def get_all(
        user: UserEntity,
    ) -> List[UserEntity]:
        """
        Return all users Superusers receive all users.
        """
        async with async_session() as session:
            return await UserRepository.get_all(user, session)

    @staticmethod
    async def get_by_clerk_id(
        clerk_id: str,
    ) -> Optional[UserEntity]:
        """
        Fetch a user by Clerk ID, return UserEntity or None.
        """
        async with async_session() as session:
            return await UserRepository.get_user_by_clerk_id(
                clerk_id=clerk_id, session=session
            )

    @staticmethod
    async def get_by_email(
        email: str,
    ) -> Optional[UserEntity]:
        """
        Fetch a user by email, return UserEntity or None.
        """
        async with async_session() as session:
            return await UserRepository.get_user_by_email(
                email=email, session=session
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
            return await UserRepository.create_user(
                session, clerk_id, email, data
            )

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
            return await UserRepository.update_user(
                session, existing, email, data
            )

    @staticmethod
    async def update_user_language(language, user):
        async with async_session() as session:
            # 1) fetch
            user = await UserRepository.get_user_by_clerk_id(
                clerk_id=user.clerk_id, session=session
            )

            # 2) update
            return await UserRepository.update_language(user, language)

    @staticmethod
    async def update_gender(gender, user):
        async with async_session() as session:
            # 1) fetch
            user = await UserRepository.get_user_by_clerk_id(
                clerk_id=user.clerk_id, session=session
            )

            # 2) update
            return await UserRepository.update_gender(user, gender)
