import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, delete, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models import User
from app.models.associations import UserSearchProfileLink
from app.schemas.user_schema import UserEntity


def _to_user_entity(user: User | UserEntity) -> UserEntity:
    return UserEntity(
        id=user.id,
        clerk_id=user.clerk_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        language=user.language,
        is_superuser=user.is_superuser,
        organization_id=user.organization_id,
        organization_name=(
            user.organization_name  # already present if it's a UserEntity
            if isinstance(user, UserEntity)
            else user.organization.name if user.organization else None
        ),
    )


def _to_user_base(user: User | UserEntity) -> User:
    return User(
        id=user.id,
        clerk_id=user.clerk_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        language=user.language,
        is_superuser=user.is_superuser,
        organization_id=user.organization_id,
    )


class UserRepository:
    @staticmethod
    async def get_user_by_clerk_id(
        clerk_id: str, session: AsyncSession
    ) -> Optional[UserEntity]:
        """
        Fetch a user by clerk ID and return as UserEntity
        including organization name.
        """
        query = (
            select(User)
            .options(selectinload(User.organization))
            .where(User.clerk_id == clerk_id)
        )
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        return _to_user_entity(user) if user else None

    @staticmethod
    async def get_by_id(user_id: uuid.UUID, session: AsyncSession) -> User:
        """
        Fetch a user by clerk ID and return as UserEntity
        including organization name.
        """
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        return user if user else None

    @staticmethod
    async def get_by_ids(
        ids: List[uuid.UUID], session: AsyncSession
    ) -> List[User]:
        """
        Fetch a user by clerk ID and return as UserEntity
        including organization name.
        """
        stmt = select(User).where(User.id.in_(ids))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create_user(
        session,
        clerk_id: str,
        email: Optional[str],
        data: Dict[str, Any],
    ) -> UserEntity:
        new_user = User(
            clerk_id=clerk_id,
            email=email,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )
        session.add(new_user)
        await session.commit()
        stmt = (
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == new_user.id)
        )
        result = await session.execute(stmt)
        user = result.scalar_one()
        return _to_user_entity(user)

    @staticmethod
    async def update_user(
        session,
        existing: UserEntity,
        email: Optional[str],
        data: Dict[str, Any],
    ) -> UserEntity | None:
        """
        Update a user’s fields if they differ from Clerk data,
        and return the updated UserEntity.
        """
        try:
            stmt = (
                select(User)
                .options(selectinload(User.organization))
                .where(User.id == existing.id)
            )
            result = await session.execute(stmt)
            user = result.scalar_one()
        except NoResultFound:
            return None

        updated = False

        if data.get("first_name") and user.first_name != data["first_name"]:
            user.first_name = data["first_name"]
            updated = True

        if data.get("last_name") and user.last_name != data["last_name"]:
            user.last_name = data["last_name"]
            updated = True

        if email and user.email != email:
            user.email = email
            updated = True

        if updated:
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return _to_user_entity(user)

    @staticmethod
    async def get_users_by_organization(
        organization_id: uuid.UUID, session: AsyncSession
    ) -> List[User]:
        """
        Return all users in the same organization, or the user itself if
        no organization.
        Superusers receive all users.
        """

        stmt = select(User).where(User.organization_id == organization_id)
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users

    @staticmethod
    async def get_all(
        user: UserEntity, session: AsyncSession
    ) -> List[UserEntity]:
        """
        Return all users in the same organization, or the user itself if
        no organization.
        Superusers receive all users.
        """
        if not user.is_superuser:
            return [user]

        stmt = select(User).options(selectinload(User.organization))
        result = await session.execute(stmt)
        users = result.scalars().all()
        return [_to_user_entity(u) for u in users]

    @staticmethod
    async def update_organization(user: User, session) -> User:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return _to_user_base(user)

    @staticmethod
    async def delete_links_for_search_profile(
        session: AsyncSession, profile_id: UUID
    ) -> None:
        stmt = delete(UserSearchProfileLink).where(
            UserSearchProfileLink.search_profile_id == profile_id
        )
        await session.execute(stmt)

    @staticmethod
    async def update_language(user: UserEntity, language: str) -> UserEntity:
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.organization))
                .where(User.id == user.id)
            )
            db_user = result.scalar_one_or_none()

            db_user.language = language
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            return _to_user_entity(db_user)
