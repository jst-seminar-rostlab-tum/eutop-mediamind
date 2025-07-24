from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict

from app.models.breaking_news import BreakingNews


class BreakingNewsItem(BaseModel):
    id: str
    image_url: Optional[str]
    url: Optional[str]
    published_at: Optional[datetime]
    language: Optional[str] = None  # e.g., "en", "de"
    headline: Optional[Dict[str, str]]  # e.g., {"en": "...", "de": "..."}
    summary: Optional[Dict[str, str]]  # e.g., {"en": "...", "de": "..."}

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, breaking_news: BreakingNews) -> "BreakingNewsItem":
        return cls(
            id=breaking_news.id,
            image_url=breaking_news.image_url,
            url=breaking_news.url,
            published_at=breaking_news.published_at,
            language=breaking_news.language,
            headline=breaking_news.headline,
            summary=breaking_news.summary,
        )


class BreakingNewsResponse(BaseModel):
    news: list[BreakingNewsItem]
    total_count: int
