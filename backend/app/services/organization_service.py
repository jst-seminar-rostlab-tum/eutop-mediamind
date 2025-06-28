import uuid
from typing import List

from fastapi import HTTPException

from app.core.db import async_session
from app.models import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.organization_schemas import (
    OrganizationCreateOrUpdate,
    OrganizationResponse,
)
from app.schemas.subscription_schemas import SubscriptionSummary
from app.schemas.user_schema import UserEntity


class OrganizationService:

    @staticmethod
    async def create_with_users(
        create_request: OrganizationCreateOrUpdate, current_user: UserEntity
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

    @staticmethod
    async def update_with_users(
        organization_id: uuid.UUID,
        update_request: OrganizationCreateOrUpdate,
        current_user: UserEntity,
    ) -> Organization:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Insufficient privileges"
            )

        async with async_session() as session:
            organization = await session.get(Organization, organization_id)
            if not organization:
                raise HTTPException(
                    status_code=404, detail="Organization not found"
                )

            # Update basic fields
            organization.name = update_request.name
            organization.email = update_request.email
            session.add(organization)

            # Get current users assigned to the organization
            current_users = await UserRepository.get_users_by_organization(
                organization_id, session
            )
            current_user_ids = {user.id for user in current_users}
            new_user_ids = set(update_request.user_ids or [])

            # Determine which users to remove and which to add
            users_to_remove = current_user_ids - new_user_ids
            users_to_add = new_user_ids - current_user_ids

            if users_to_remove:
                users = await UserRepository.get_by_ids(
                    list(users_to_remove), session
                )
                for user in users:
                    user.organization_id = None
                    await UserRepository.update_organization(user, session)

            if users_to_add:
                users = await UserRepository.get_by_ids(
                    list(users_to_add), session
                )
                for user in users:
                    user.organization_id = organization.id
                    await UserRepository.update_organization(user, session)

            await session.commit()
            await session.refresh(organization)
            return organization

    @staticmethod
    async def delete_organization(
        organization_id: uuid.UUID,
        current_user: UserEntity,
    ) -> Organization:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Insufficient privileges"
            )

        async with async_session() as session:
            organization = await session.get(Organization, organization_id)
            if not organization:
                raise HTTPException(
                    status_code=404, detail="Organization not found"
                )

            # Find all users currently assigned to the organization
            users = await UserRepository.get_users_by_organization(
                organization_id, session
            )
            for user in users:
                user.organization_id = None
                await UserRepository.update_organization(user, session)

            # Delete the organization
            await session.delete(organization)
            await session.commit()
            return organization

    @staticmethod
    async def set_subscriptions_from_summary(
        organization_id: uuid.UUID,
        subscriptions: list[SubscriptionSummary],
    ) -> list[SubscriptionSummary]:
        async with async_session() as session:
            # Ensure org exists
            organization = await session.get(Organization, organization_id)
            if not organization:
                raise HTTPException(
                    status_code=404, detail="Organization not found"
                )

            await OrganizationRepository.update_subscriptions(
                organization_id, subscriptions, session
            )

            # Fetch and return updated summaries
            return await OrganizationRepository.get_subscription_summaries(
                organization_id, session
            )

    @staticmethod
    async def get_all_with_users(
        current_user: UserEntity,
    ) -> List[OrganizationResponse]:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Insufficient privileges"
            )
        async with async_session() as session:
            return await OrganizationRepository.get_all_with_users(session)
