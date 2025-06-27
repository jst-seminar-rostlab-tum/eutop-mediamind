import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, TIMESTAMP, Integer, Sequence
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models import Match
    from app.models.report import Report

counter_seq = Sequence("matching_run_counter_seq", metadata=SQLModel.metadata)

class MatchingRun(SQLModel, table=True):
    __tablename__ = "matching_runs"
    """
    Represents a matching run for a search profile.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            default=datetime.now(timezone.utc),
        )
    )

    counter: int = Field(
        sa_column=Column(
            Integer,
            counter_seq,
            server_default=counter_seq.next_value(),
            nullable=False,
            unique=True,
        )
    )

    algorithm_version: Optional[str] = None

    matches: List["Match"] = Relationship(back_populates="matching_run")
    reports: List["Report"] = Relationship(back_populates="matching_run")
