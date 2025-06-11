import uuid
from typing import Sequence

from sqlalchemy import delete
from sqlmodel import select

from app.core.db import async_session
from app.models import ArticleKeywordLink, Match, SearchProfile
from app.repositories.search_profile_repository import SearchProfileRepository


class ArticleMatchingService:
    """Service for matching articles"""

    async def run(self, page_size: int = 100) -> None:
        """Run the article matching process."""

        return None
