from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models import User
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
            user.organization.name if user.organization else None
        ),
    )


async def get_user_by_clerk_id(clerk_id: str) -> Optional[UserEntity]:
    """
    Fetch a user by clerk ID and return as UserEntity
    including organization name.
    """
    async with async_session() as session:
        query = (
            select(User)
            .options(selectinload(User.organization))
            .where(User.clerk_id == clerk_id)
        )
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        return _to_user_entity(user) if user else None


async def update_user(user_public: UserEntity) -> UserEntity:
    """
    Update a user in the database using a UserEntity object and
    return the updated UserEntity.
    """
    async with async_session() as session:
        try:
            result = await session.execute(
                select(User)
                .options(selectinload(User.organization))
                .where(User.id == user_public.id)
            )
            user = result.scalar_one()
        except NoResultFound:
            raise ValueError(f"User with id {user_public.id} not found")

        # Update fields
        user.email = user_public.email
        user.first_name = user_public.first_name
        user.last_name = user_public.last_name
        user.is_superuser = user_public.is_superuser
        user.organization_id = user_public.organization_id

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return _to_user_entity(user)


async def create_user(user: User) -> UserEntity:
    """
    Create a new user in the database and return as UserEntity.
    """
    async with async_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return _to_user_entity(user)


async def get_user_list_from_organization(
    user: User,
) -> Union[list[User], User]:
    """
    Return all users in the same organization, or the user itself if
    no organization.
    Superusers receive all users.
    """
    async with async_session() as session:
        if user.is_superuser:
            query = select(User)
        elif user.organization_id is None:
            return user
        else:
            query = select(User).where(
                User.organization_id == user.organization_id
            )

        users = await session.execute(query)
        return users.scalars().all()


async def update_language(user: UserEntity, language: str) -> UserEntity:
    async with async_session() as session:
        user.language = language
        session.add(user)
        session.commit()
        session.refresh(user)
        return _to_user_entity(user)
