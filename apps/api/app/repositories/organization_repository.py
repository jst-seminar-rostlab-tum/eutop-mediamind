from typing import List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Organization, Subscription
from app.models.associations import OrganizationSubscriptionLink
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.organization_schemas import OrganizationResponse
from app.schemas.subscription_schemas import SubscriptionSummary


class OrganizationRepository:
    @staticmethod
    async def create(
        organization: Organization, session: AsyncSession
    ) -> Organization:
        session.add(organization)
        await session.flush()
        return organization

    @staticmethod
    async def update_subscriptions(
        organization_id: UUID,
        subscriptions: List[SubscriptionSummary],
        session: AsyncSession,
    ) -> None:
        # Get current subscription IDs for the organization
        result = await session.execute(
            select(OrganizationSubscriptionLink.subscription_id).where(
                OrganizationSubscriptionLink.organization_id == organization_id
            )
        )
        current_sub_ids = {row[0] for row in result.fetchall()}

        to_add = {
            s.id
            for s in subscriptions
            if s.is_subscribed and s.id not in current_sub_ids
        }
        to_remove = {
            s.id
            for s in subscriptions
            if not s.is_subscribed and s.id in current_sub_ids
        }

        # Add new
        for sub_id in to_add:
            session.add(
                OrganizationSubscriptionLink(
                    organization_id=organization_id, subscription_id=sub_id
                )
            )

        # Remove old
        if to_remove:
            await session.execute(
                delete(OrganizationSubscriptionLink).where(
                    OrganizationSubscriptionLink.organization_id
                    == organization_id,
                    OrganizationSubscriptionLink.subscription_id.in_(
                        List[to_remove]
                    ),
                )
            )

        await session.commit()

    @staticmethod
    async def get_subscription_summaries(
        organization_id: UUID,
        session: AsyncSession,
    ) -> list[SubscriptionSummary]:
        # Get all subscriptions with info if they are assigned
        result = await session.execute(
            select(
                Subscription.id,
                Subscription.name,
                OrganizationSubscriptionLink.subscription_id.isnot(None).label(
                    "is_subscribed"
                ),
            ).outerjoin(
                OrganizationSubscriptionLink,
                (
                    Subscription.id
                    == OrganizationSubscriptionLink.subscription_id
                )
                & (
                    OrganizationSubscriptionLink.organization_id
                    == organization_id
                ),
            )
        )
        rows = result.fetchall()

        return [
            SubscriptionSummary(id=row[0], name=row[1], is_subscribed=row[2])
            for row in rows
        ]

    @staticmethod
    async def get_with_users(
        session: AsyncSession,
        organization_id: UUID,
    ) -> OrganizationResponse | None:
        result = await session.execute(
            select(Organization)
            .where(Organization.id == organization_id)
            .options(selectinload(Organization.users))
        )
        org = result.scalars().first()
        if org is None:
            return None

        subscriptions = (
            await (
                SubscriptionRepository.get_all_subscriptions_with_organization(
                    session,
                    org.id,
                )
            )
        )

        return OrganizationResponse(
            id=org.id,
            name=org.name,
            email=org.email,
            pdf_as_link=org.pdf_as_link,
            users=org.users,
            subscriptions=subscriptions,
        )

    @staticmethod
    async def get_all_with_users(
        session: AsyncSession,
    ) -> List[OrganizationResponse]:
        result = await session.execute(
            select(Organization).options(
                selectinload(Organization.users)
            )  # eager load users
        )
        organizations = result.scalars().all()

        responses = []
        for org in organizations:
            subscriptions = await SubscriptionRepository.get_all_subscriptions_with_organization(  # noqa: E501
                session, org.id
            )

            responses.append(
                OrganizationResponse(
                    id=org.id,
                    name=org.name,
                    email=org.email,
                    pdf_as_link=org.pdf_as_link,
                    users=org.users,
                    subscriptions=subscriptions,
                )
            )

        return responses
