import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
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
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    time_slot: str = Field(
        max_length=32, nullable=True
    )  # e.g., "morning", "afternoon", "evening"
    s3_key: str = Field(max_length=512, nullable=False)
    status: ReportStatus = Field(default=ReportStatus.PENDING, nullable=False)

    # Relationships
    search_profile: Optional["SearchProfile"] = Relationship(
        back_populates="reports"
    )
