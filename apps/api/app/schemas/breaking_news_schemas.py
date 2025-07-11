from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.breaking_news import BreakingNews


class BreakingNewsItem(BaseModel):
    id: str
    title: Optional[str]
    summary: Optional[str]
    image_url: Optional[str]
    url: Optional[str]
    published_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, breaking_news: BreakingNews) -> "BreakingNewsItem":
        return cls(
            id=breaking_news.id,
            title=breaking_news.title,
            summary=breaking_news.summary,
            image_url=breaking_news.image_url,
            url=breaking_news.url,
            published_at=breaking_news.published_at,
        )


class BreakingNewsResponse(BaseModel):
    news: list[BreakingNewsItem]
    total_count: int
