import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import TIMESTAMP, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import Match
    from app.models.report import Report


class MatchingRun(SQLModel, table=True):
    __tablename__ = "matching_runs"
    """
    Represents a matching run for a search profile.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
        )
    )

    algorithm_version: Optional[str] = None

    matches: List["Match"] = Relationship(back_populates="matching_run")
    reports: List["Report"] = Relationship(back_populates="matching_run")
