from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_session

from app.models import User


class UserCreate(BaseModel):
    email_address: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


class AuthService:
    @staticmethod
    async def create_user(user_in: UserCreate) -> User:
        async with async_session() as session:
            user = User(
                id=user_in.clerk_id,
                email=user_in.email,
                first_name=user_in.first_name,
                last_name=user_in.last_name,
                is_superuser=user_in.is_superuser,
                organization_id=user_in.organization_id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
