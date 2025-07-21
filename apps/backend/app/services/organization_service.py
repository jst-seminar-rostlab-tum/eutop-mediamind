import uuid
from typing import List

from fastapi import HTTPException

from app.core.db import async_session
from app.models import Organization
from app.models.user import UserRole
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.organization_schemas import (
    CreateRequestUser,
    OrganizationCreateOrUpdate,
    OrganizationResponse,
)
from app.schemas.subscription_schemas import SubscriptionSummary
from app.schemas.user_schema import UserEntity


class OrganizationService:

    @staticmethod
    async def create_with_users(
        create_request: OrganizationCreateOrUpdate,
    ) -> OrganizationResponse:
        async with async_session() as session:
            organization = (
                await OrganizationService._create_organization_from_request(
                    create_request, session
                )
            )

            if create_request.users:
                await OrganizationService._assign_users_to_organization(
                    create_request.users, organization.id, session
                )

            await session.commit()
            await session.refresh(organization)

            users = await UserRepository.get_users_by_organization(
                organization.id, session
            )
            return OrganizationService._build_response(organization, users)

    @staticmethod
    async def update_with_users(
        organization_id: uuid.UUID,
        update_request: OrganizationCreateOrUpdate,
    ) -> OrganizationResponse:
        async with async_session() as session:
            organization = await session.get(Organization, organization_id)
            if not organization:
                raise HTTPException(
                    status_code=404, detail="Organization not found"
                )

            organization.name = update_request.name
            if update_request.email:
                organization.email = update_request.email
            organization.pdf_as_link = update_request.pdf_as_link
            session.add(organization)

            await OrganizationService._sync_user_assignments(
                organization_id, update_request.users, session
            )

            await session.commit()
            await session.refresh(organization)

            updated_users = await UserRepository.get_users_by_organization(
                organization.id, session
            )
            return OrganizationService._build_response(
                organization, updated_users
            )

    @staticmethod
    async def delete_organization(organization_id: uuid.UUID):
        async with async_session() as session:
            organization = await session.get(Organization, organization_id)
            if not organization:
                raise HTTPException(
                    status_code=404, detail="Organization not found"
                )

            users = await UserRepository.get_users_by_organization(
                organization_id, session
            )
            for user in users:
                user.organization_id = None
                await UserRepository.update_organization(user, session)

            await session.delete(organization)
            await session.commit()

    @staticmethod
    async def set_subscriptions_from_summary(
        organization_id: uuid.UUID,
        subscriptions: list[SubscriptionSummary],
    ) -> list[SubscriptionSummary]:
        async with async_session() as session:
            organization = await session.get(Organization, organization_id)
            if not organization:
                raise HTTPException(
                    status_code=404, detail="Organization not found"
                )

            await OrganizationRepository.update_subscriptions(
                organization_id, subscriptions, session
            )
            return await OrganizationRepository.get_subscription_summaries(
                organization_id, session
            )

    @staticmethod
    async def get_with_users(
        organization_id: uuid.UUID, current_user: UserEntity
    ) -> List[OrganizationResponse]:
        if current_user.role != "maintainer" and not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Insufficient privileges"
            )
        async with async_session() as session:
            return await OrganizationRepository.get_with_users(
                session, organization_id
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

    @staticmethod
    async def _create_organization_from_request(
        request: OrganizationCreateOrUpdate, session
    ) -> Organization:
        organization = Organization(
            name=request.name,
            email=request.email,
            pdf_as_link=request.pdf_as_link,
        )
        return await OrganizationRepository.create(organization, session)

    @staticmethod
    async def _assign_users_to_organization(
        users: List[CreateRequestUser], organization_id: uuid.UUID, session
    ):
        role_map = {u.id: u.role for u in users}
        user_ids = list(role_map.keys())

        db_users = await UserRepository.get_by_ids(user_ids, session)
        for user in db_users:
            user.organization_id = organization_id
            user.role = role_map.get(user.id, UserRole.member)
            await UserRepository.update_organization(user, session)

    @staticmethod
    async def _sync_user_assignments(
        organization_id: uuid.UUID,
        requested_users: List[CreateRequestUser],
        session,
    ):
        existing_users = await UserRepository.get_users_by_organization(
            organization_id, session
        )
        existing_map = {u.id: u for u in existing_users}
        requested_map = {u.id: u.role for u in requested_users}

        existing_ids = set(existing_map.keys())
        requested_ids = set(requested_map.keys())

        to_remove = existing_ids - requested_ids
        to_add = requested_ids - existing_ids
        to_update = existing_ids & requested_ids

        if to_remove:
            users = await UserRepository.get_by_ids(list(to_remove), session)
            for user in users:
                user.organization_id = None
                user.role = UserRole.member
                await UserRepository.update_organization(user, session)

        if to_add:
            users = await UserRepository.get_by_ids(list(to_add), session)
            for user in users:
                user.organization_id = organization_id
                user.role = requested_map.get(user.id, UserRole.member)
                await UserRepository.update_organization(user, session)

        for uid in to_update:
            user = existing_map[uid]
            new_role = requested_map.get(uid)
            if user.role != new_role:
                user.role = new_role
                await UserRepository.update_organization(user, session)

    @staticmethod
    def _build_response(
        organization: Organization, users: list[UserEntity]
    ) -> OrganizationResponse:
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            email=organization.email,
            pdf_as_link=organization.pdf_as_link,
            users=users,
        )
