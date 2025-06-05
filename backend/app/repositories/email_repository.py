from app.models.email import Email, EmailState
from app.core.db import async_session
from sqlalchemy import select
from uuid import UUID


class EmailRepository:

    @staticmethod
    async def add_email(email: Email) -> Email:
        async with async_session() as session:
            session.add(email)
            session.commit()
            session.refresh(email)
            return email

    @staticmethod
    async def get_email_by_id(email_id: UUID) -> Email|None:
        async with async_session() as session:
            return await session.get(Email, email_id)

    @staticmethod
    async def get_all_unsent_emails() -> list[Email]:
        async with async_session() as session:
            query = select(Email).where(Email.state == (EmailState.PENDING or EmailState.RETRY))
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def update_email(email: Email) -> Email|None:
        async with async_session() as session:
            existing_email = session.get(Email, email.id)
            if existing_email:
                for attr, value in vars(email).items():
                    if attr != "_sa_instance_state":
                        setattr(existing_email, attr, value)
                session.commit()
                session.refresh(existing_email)
                return existing_email
            else:
                return None

