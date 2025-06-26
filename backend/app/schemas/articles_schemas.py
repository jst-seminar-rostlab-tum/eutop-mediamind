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
            id=article.id,
            title=article.title,
            content=article.content,
            url=article.url,
            image_url=article.image_url,
            authors=article.authors,
            published_at=article.published_at,
            language=article.language,
            categories=article.categories,
            summary=article.summary,
            title_en=article.title_en,
            title_de=article.title_de,
            content_en=article.content_en,
            content_de=article.content_de,
            summary_en=article.summary_en,
            summary_de=article.summary_de,
            crawled_at=article.crawled_at,
            scraped_at=article.scraped_at,
            sorting_order=match.sorting_order,
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
