import uuid

from sqlmodel import Field, SQLModel


class BreakingNews(SQLModel, table=False):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    title: str = Field(default=None, nullable=True)
    summary: str = Field(default=None, nullable=True)
    image_url: str = Field(default=None, nullable=True)
    url: str = Field(default=None, nullable=True)
    published_at: str = Field(default=None, nullable=True)
