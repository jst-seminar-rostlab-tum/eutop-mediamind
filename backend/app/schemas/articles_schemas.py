from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import Match


class ArticleOverviewItem(BaseModel):
    id: UUID
    title: str
    url: str
    author: str
    published_at: datetime
    language: str
    category: str
    summary: str | None
    sorting_order: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, match: Match) -> "ArticleOverviewItem":
        article = match.article
        return cls(
            id=article.id,
            title=article.title,
            url=article.url,
            author=article.author,
            published_at=article.published_at,
            language=article.language,
            category=article.category,
            summary=article.summary,
            sorting_order=match.sorting_order,
        )


class MatchArticleContent(BaseModel):
    headline: dict[str, str]
    summary: dict[str, str]
    text: dict[str, str]
    image_urls: list[str]
    published: datetime
    crawled: datetime


class MatchTopicItem(BaseModel):
    id: UUID
    name: str
    score: float
    keywords: list[str] | None = None


class MatchItem(BaseModel):
    id: UUID
    relevance: float
    topic: list[MatchTopicItem]
    article: MatchArticleContent

    @classmethod
    def from_entity(
        cls,
        match: Match,
        topic_scores: dict[UUID, float],
        topic_keywords: dict[UUID, list[str]] | None = None,
        relevance: float = 0.0,
        topic_id_to_name: dict[UUID, str] | None = None,
    ) -> "MatchItem":
        a = match.article
        return cls(
            id=match.id,
            relevance=relevance,
            topic=(
                [
                    MatchTopicItem(
                        id=tid,
                        name=(
                            topic_id_to_name.get(tid, "")
                            if topic_id_to_name
                            else ""
                        ),
                        keywords=(
                            topic_keywords.get(tid) if topic_keywords else None
                        ),
                        score=score,
                    )
                    for tid, score in topic_scores.items()
                ]
            ),
            article=MatchArticleContent(
                headline={
                    "de": a.title or "",
                    "en": a.title or "",
                },  # need to implement language handling
                summary={"de": a.summary or "", "en": ""},
                text={"de": a.content or "", "en": ""},
                image_urls=["https://example.com/image.jpg"]  # placeholder
                or [],  # need to implement image extraction in scraping
                published=a.published_at,
                crawled=a.crawled_at,
            ),
        )


class ArticleOverviewResponse(BaseModel):
    matches: list[MatchItem]


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
