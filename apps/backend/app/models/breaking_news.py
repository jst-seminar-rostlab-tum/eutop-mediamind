# flake8: noqa
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class BreakingNews(SQLModel, table=False):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True,
    )
    headline: Optional[dict] = Field(
        sa_column=Column(
            JSON,
            nullable=True,
            default=None,
            comment="Headline in different languages, e.g., {'en': '...', 'de': '...'}",
        )
    )
    summary: Optional[dict] = Field(
        sa_column=Column(
            JSON,
            nullable=True,
            default=None,
            comment="Summary in different languages, e.g., {'en': '...', 'de': '...'}",
        )
    )
    image_url: str = Field(default=None, nullable=True)
    url: str = Field(default=None, nullable=True)
    published_at: str = Field(default=None, nullable=True)
    relevance_score: float = Field(default=0.0, nullable=True)
    language: str = Field(default=None, nullable=True)
