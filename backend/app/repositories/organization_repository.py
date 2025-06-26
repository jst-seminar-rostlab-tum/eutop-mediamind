from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import async_session
from app.schemas.organization_schemas import Organization, OrganizationCreate


class OrganizationRepository:
    @staticmethod
    async def create(
        organization: Organization, session: AsyncSession
    ) -> Organization:
        session.add(organization)
        await session.flush()
        return organization
