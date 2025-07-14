from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session
from app.models import SearchProfile
from app.models.email import Email, EmailState


class EmailRepository:

    @staticmethod
    async def add_email(email: Email) -> Email:
        async with async_session() as session:
            session.add(email)
            await session.commit()
            await session.refresh(email)
            return email

    @staticmethod
    async def get_email_by_id(email_id: UUID) -> Email | None:
        async with async_session() as session:
            return await session.get(Email, email_id)

    @staticmethod
    async def get_all_unsent_emails() -> list[Email]:
        async with async_session() as session:
            query = (
                select(Email)
                .where(Email.state == (EmailState.PENDING or EmailState.RETRY))
                .options(selectinload(Email.report))
            )
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def update_emails(
        profile_id: UUID,
        organization_emails: List[str],
        profile_emails: List[str],
        session: AsyncSession,
    ) -> None:
        # bulk‐update the two list-columns in one go
        await session.execute(
            update(SearchProfile)
            .where(SearchProfile.id == profile_id)
            .values(
                organization_emails=organization_emails,
                profile_emails=profile_emails,
            )
        )
        await session.flush()

    @staticmethod
    async def update_email(email: Email) -> Email | None:
        async with async_session() as session:
            existing_email = await session.get(Email, email.id)
            if existing_email:
                for attr, value in vars(email).items():
                    if attr != "_sa_instance_state":
                        setattr(existing_email, attr, value)
                await session.commit()
                await session.refresh(existing_email)
                return existing_email
            else:
                return None
