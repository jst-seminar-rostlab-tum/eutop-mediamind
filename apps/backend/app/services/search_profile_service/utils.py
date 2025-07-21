from datetime import datetime, timedelta, timezone

from app.models import SearchProfile, Topic
from app.repositories.match_repository import MatchRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.search_profile_schemas import SearchProfileDetailResponse
from app.schemas.topic_schemas import TopicResponse
from app.schemas.user_schema import UserEntity


async def _build_profile_response(
    profile: SearchProfile,
    current_user: UserEntity,
) -> SearchProfileDetailResponse:
    is_owner = profile.created_by_id == current_user.id
    is_editor = (
        current_user.id == profile.owner_id
        or current_user.is_superuser
        or current_user.id in (profile.can_edit_user_ids or [])
    )
    is_reader = (
        current_user.id == profile.owner_id
        or current_user.is_superuser
        or current_user.id in (profile.can_read_user_ids or [])
    )
    org_emails = profile.organization_emails or []
    prof_emails = profile.profile_emails or []
    topics = [_build_topic_response(t) for t in profile.topics]
    subscriptions = (
        await SubscriptionRepository.get_all_subscriptions_with_search_profile(
            profile.id
        )
    )
    time_th = datetime.now(timezone.utc) - timedelta(hours=24)
    new_count = await MatchRepository.get_recent_match_count_by_profile_id(
        profile.id, time_th
    )

    return SearchProfileDetailResponse(
        id=profile.id,
        name=profile.name,
        is_public=profile.is_public,
        owner_id=profile.created_by_id,
        is_owner=is_owner,
        can_read_user_ids=profile.can_read_user_ids or [],
        is_reader=is_reader,
        can_edit_user_ids=profile.can_edit_user_ids or [],
        is_editor=is_editor,
        organization_emails=org_emails,
        profile_emails=prof_emails,
        topics=topics,
        subscriptions=subscriptions,
        new_articles_count=new_count,
    )


def _build_topic_response(
    topic: Topic,
) -> TopicResponse:
    return TopicResponse(
        id=topic.id,
        name=topic.name,
        keywords=[kw.name for kw in topic.keywords],
    )
