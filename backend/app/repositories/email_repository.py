from sqlalchemy.ext.asyncio import async_session
from app.models.email import Email, EmailState


class EmailRepository:

    @staticmethod
    async def add_email(email: Email) -> Email:
        async with async_session() as session:
            session.add(email)
            session.commit()
            session.refresh(email)
            return email

    @staticmethod
    async def get_all_unsent_emails() -> list[Email]:
        async with async_session() as session:
            result = (session
                .query(Email)
                .where(Email.state == EmailState.PENDING or EmailState.RETRY))
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

