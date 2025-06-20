from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from app.models import User
from app.schemas.user_schema import UserEntity


def _to_entity(user: User) -> UserEntity:
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


async def get_user_by_clerk_id(
    session,
    clerk_id: str,
) -> Optional[UserEntity]:
    stmt = (
        select(User)
        .options(selectinload(User.organization))
        .where(User.clerk_id == clerk_id)
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return _to_entity(user) if user else None


async def get_user_list_by_org(
    session,
    user: UserEntity,
) -> Union[List[UserEntity], UserEntity]:
    if user.is_superuser:
        stmt = select(User)
    elif user.organization_id is None:
        return user
    else:
        stmt = select(User).where(User.organization_id == user.organization_id)
    stmt = stmt.options(selectinload(User.organization))
    result = await session.execute(stmt)
    users = result.scalars().all()
    return [_to_entity(u) for u in users]


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
    return _to_entity(user)


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

    return _to_entity(user)
