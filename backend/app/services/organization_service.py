from fastapi import HTTPException
from app import models
from app.core.db import async_session
from app.models import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.organization_schemas import OrganizationCreate
from app.schemas.user_schema import UserEntity


class OrganizationService:

    @staticmethod
    async def create_with_users(
        create_request: OrganizationCreate, current_user: UserEntity
    ) -> Organization:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Insufficient privileges"
            )
        async with async_session() as session:
            organization = Organization(
                name=create_request.name, email=create_request.email
            )
            organization = await OrganizationRepository.create(
                organization, session=session
            )

            if create_request.user_ids:
                users = await UserRepository.get_by_ids(
                    create_request.user_ids, session
                )
                for user in users:
                    user.organization_id = organization.id
                    await UserRepository.update_organization(user, session)
            await session.commit()
            await session.refresh(organization)
            return organization
