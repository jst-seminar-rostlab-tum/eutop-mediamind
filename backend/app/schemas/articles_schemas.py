from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import Match


class ArticleOverviewItem(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    url: str
    image_url: Optional[str]
    authors: Optional[List[str]]
    published_at: datetime
    language: Optional[str]
    categories: Optional[List[str]]
    summary: Optional[str]
    title_en: Optional[str]
    title_de: Optional[str]
    content_en: Optional[str]
    content_de: Optional[str]
    summary_en: Optional[str]
    summary_de: Optional[str]
    crawled_at: datetime
    scraped_at: Optional[datetime]
    sorting_order: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, match: Match) -> "ArticleOverviewItem":
        article = match.article
        return cls(
            id=getattr(article, "id"),
            title=getattr(article, "title", ""),
            content=getattr(article, "content", None),
            url=getattr(article, "url"),
            image_url=getattr(article, "image_url", None),
            authors=getattr(article, "authors", None),
            published_at=getattr(article, "published_at"),
            language=getattr(article, "language", None),
            categories=getattr(article, "categories", None),
            summary=getattr(article, "summary", None),
            title_en=getattr(article, "title_en", None),
            title_de=getattr(article, "title_de", None),
            content_en=getattr(article, "content_en", None),
            content_de=getattr(article, "content_de", None),
            summary_en=getattr(article, "summary_en", None),
            summary_de=getattr(article, "summary_de", None),
            crawled_at=getattr(article, "crawled_at"),
            scraped_at=getattr(article, "scraped_at", None),
            sorting_order=getattr(match, "sorting_order"),
        )


class ArticleOverviewResponse(BaseModel):
    search_profile_id: UUID
    articles: list[ArticleOverviewItem]


class MatchDetailResponse(BaseModel):
    match_id: UUID
    comment: str | None
    sorting_order: int

    article_id: UUID
    title: str
    url: str
    author: str
    published_at: datetime
    language: str
    category: str
    summary: str | None

    model_config = ConfigDict(from_attributes=True)
