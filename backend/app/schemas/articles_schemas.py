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
        relevance: float = 0.0,
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
                            match.topic.name
                            if match.topic and match.topic.id == tid
                            else ""
                        ),
                        score=score,
                    )
                    for tid, score in topic_scores.items()
                ]
                if match.topic
                else []
            ),
            article=MatchArticleContent(
                headline={
                    "de": a.title or "",
                    "en": a.title or "",
                },  # need to implement language handling
                summary={"de": a.summary or "", "en": a.summary or ""},
                text={"de": a.content or "", "en": a.content or ""},
                image_urls=[]
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
