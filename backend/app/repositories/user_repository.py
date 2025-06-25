from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User
from app.schemas.user_schema import UserEntity


def _to_user_entity(user: User) -> UserEntity:
    return UserEntity(
        id=user.id,
        clerk_id=user.clerk_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_superuser=user.is_superuser,
        organization_id=user.organization_id,
        organization_name=(
            user.organization.name if user.organization else None
        ),
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
    async def get_users_by_user_organization(
        user: UserEntity, session: AsyncSession
    ) -> List[UserEntity]:
        """
        Return all users in the same organization, or the user itself if
        no organization.
        Superusers receive all users.
        """
        if (not user.is_superuser) & (user.organization_id is None):
            return [user]
        if user.is_superuser:
            stmt = select(User).options(selectinload(User.organization))
        else:
            stmt = select(User).where(
                User.organization_id == user.organization_id
            )
        stmt = stmt.options(selectinload(User.organization))
        result = await session.execute(stmt)
        users = result.scalars().all()
        return [_to_user_entity(u) for u in users]
