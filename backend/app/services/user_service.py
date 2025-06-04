from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import engine
from app.models import User
from app.repositories.user_repository import get_user_list_from_organization

async_session = async_sessionmaker(engine, expire_on_commit=False)


class UserService:
    @staticmethod
    async def list_users(user: User) -> list[User] | User:
        return await get_user_list_from_organization(user)

    @staticmethod
    def get_current_user_info(current_user: User) -> User:
        return current_user