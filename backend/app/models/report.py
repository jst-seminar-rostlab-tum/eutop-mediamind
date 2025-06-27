import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import TIMESTAMP, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .matching_runs import MatchingRun
    from .search_profile import SearchProfile


class ReportStatus(Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"


class Report(SQLModel, table=True):
    __tablename__ = "reports"
    # Attributes
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    search_profile_id: uuid.UUID = Field(foreign_key="search_profiles.id")

    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
        )
    )
    time_slot: str = Field(
        max_length=32, nullable=True
    )  # e.g., "morning", "afternoon", "evening"
    s3_key: str = Field(max_length=512, nullable=False)
    status: ReportStatus = Field(default=ReportStatus.PENDING, nullable=False)
    matching_runs_id: Optional[uuid.UUID] = Field(
        foreign_key="matching_runs.id", nullable=True
    )
    language: str = Field(max_length=255, nullable=False, default="en")

    # Relationships
    search_profile: Optional["SearchProfile"] = Relationship(
        back_populates="reports"
    )
    matching_run: Optional["MatchingRun"] = Relationship(
        back_populates="reports"
    )
