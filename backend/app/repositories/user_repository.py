from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import engine
from app.models import User

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_user_by_clerk_id(clerk_id) -> User:
    async with async_session() as session:
        query = select(User).where(User.clerk_id == clerk_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def update_user(user: User) -> User:
    async with async_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def create_user(user: User) -> User:
    async with async_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def get_user_list_from_organization(user: User) -> list[User] | User:
    async with async_session() as session:
        if user.is_superuser:
            query = select(User)
        elif user.organization_id is None:
            return user
        else:
            query = select(User).where(User.organization_id == user.organization_id)

        result = await session.execute(query)
        return result.scalars().all()
