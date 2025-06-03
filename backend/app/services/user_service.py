from clerk_backend_api import Clerk
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import configs
from app.core.db import engine
from app.models import User
from app.models.user import UserCreate

async_session = async_sessionmaker(engine, expire_on_commit=False)


class UserService:
    @staticmethod
    async def list_users() -> list:
        async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            return await clerk.users.list_async()

    @staticmethod
    async def create_user_if_not_exists(user_in: UserCreate) -> User:
        async with async_session() as session:
            query = select(User).where(User.clerk_id == user_in.clerk_id)
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                user_data = user_in.model_dump()
                model_fields = {
                    c.key for c in inspect(User).mapper.column_attrs
                }
                updated = False

                for field in model_fields:
                    if (
                        field in user_data
                        and getattr(existing_user, field) != user_data[field]
                        and field != "organization_id"
                    ):
                        setattr(existing_user, field, user_data[field])
                        updated = True

                if updated:
                    session.add(existing_user)
                    await session.commit()
                    await session.refresh(existing_user)

                return existing_user

            # Create new user
            user = User(**user_in.model_dump())
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    def get_current_user_info(current_user: User) -> User:
        return current_user
