from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class BreakingNews(SQLModel, table=False):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
    )
    title: str = Field(default=None, nullable=True)
    summary: str = Field(default=None, nullable=True)
    image_url: str = Field(default=None, nullable=True)
    url: str = Field(default=None, nullable=True)
    published_at: str = Field(default=None, nullable=True)
    relevance_score: float = Field(default=0.0, nullable=True)
    language: str = Field(default=None, nullable=True)
