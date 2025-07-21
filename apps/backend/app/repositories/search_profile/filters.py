from sqlalchemy import and_, or_, true

from app.models import SearchProfile, User
from app.models.user import UserRole


def user_access_filter(
    user_id: str,
    organization_id: str,
    role: UserRole,
    is_superuser: bool,
):
    """
    Build a SQL condition to filter SearchProfiles based on user access:
    - superuser: all profiles
    - maintainer: all profiles in org
    - default: owned, subscribed, public in organization
    """
    if is_superuser:
        return true()

    if role == UserRole.maintainer:
        return SearchProfile.organization_id == organization_id

    return or_(
        SearchProfile.created_by_id == user_id,
        SearchProfile.users.any(User.id == user_id),
        and_(
            SearchProfile.organization_id == organization_id,
            SearchProfile.is_public,
        ),
    )


def base_load_options():
    """
    Return default load options to eagerly fetch users and
    topics with keywords.
    """
    from sqlalchemy.orm import selectinload

    from app.models.topic import Topic

    return [
        selectinload(SearchProfile.users),
        selectinload(SearchProfile.topics).selectinload(Topic.keywords),
    ]
