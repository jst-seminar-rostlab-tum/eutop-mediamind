from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


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

    class Config:
        orm_mode = True


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

    class Config:
        orm_mode = True

