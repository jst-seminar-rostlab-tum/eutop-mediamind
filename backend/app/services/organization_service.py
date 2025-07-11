import uuid
from typing import List

from fastapi import HTTPException

from app.core.db import async_session
from app.models import Organization
from app.models.user import UserRole
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
    ) -> OrganizationResponse:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Insufficient privileges"
            )

        async with async_session() as session:
            organization = Organization(
                name=create_request.name,
                email=create_request.email,
                pdf_as_link=create_request.pdf_as_link,
            )
            organization = await OrganizationRepository.create(
                organization, session=session
            )

            # Only process if there are user assignments
            if len(create_request.users) > 0:
                # Build mapping of user IDs to roles in one pass
                role_map = {u.id: u.role for u in create_request.users}
                user_ids = list(role_map.keys())

                # Fetch and update each user
                users = await UserRepository.get_by_ids(user_ids, session)
                for user in users:
                    user.organization_id = organization.id
                    user.role = role_map.get(user.id, UserRole.member)
                    await UserRepository.update_organization(user, session)

            await session.commit()
            await session.refresh(organization)

            users = await UserRepository.get_users_by_organization(
                organization.id, session
            )
            return OrganizationResponse(
                id=organization.id,
                name=organization.name,
                email=organization.email,
                pdf_as_link=organization.pdf_as_link,
                users=users,
            )

    @staticmethod
    async def update_with_users(
        organization_id: uuid.UUID,
        update_request: OrganizationCreateOrUpdate,
        current_user: UserEntity,
    ) -> OrganizationResponse:
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
            if update_request.email:
                organization.email = update_request.email
            organization.pdf_as_link = update_request.pdf_as_link
            session.add(organization)

            # Get current users in the organization
            existing_users = await UserRepository.get_users_by_organization(
                organization_id, session
            )
            existing_ids = {u.id for u in existing_users}

            # Build mapping of new user IDs to roles in one pass
            role_map = {u.id: u.role for u in update_request.users}
            new_ids = set(role_map.keys())

            # Determine removals and additions
            to_remove = existing_ids - new_ids
            to_add = new_ids - existing_ids

            # Remove users no longer assigned
            if to_remove:
                users = await UserRepository.get_by_ids(
                    list(to_remove), session
                )
                for user in users:
                    user.organization_id = None
                    user.role = UserRole.member
                    await UserRepository.update_organization(user, session)

            # Add new users
            if to_add:
                users = await UserRepository.get_by_ids(list(to_add), session)
                for user in users:
                    user.organization_id = organization.id
                    user.role = role_map.get(user.id, UserRole.member)
                    await UserRepository.update_organization(user, session)

            await session.commit()
            await session.refresh(organization)

            users = await UserRepository.get_users_by_organization(
                organization.id, session
            )
            return OrganizationResponse(
                id=organization.id,
                name=organization.name,
                email=organization.email,
                pdf_as_link=organization.pdf_as_link,
                users=users,
            )

    @staticmethod
    async def delete_organization(
        organization_id: uuid.UUID,
        current_user: UserEntity,
    ):
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
