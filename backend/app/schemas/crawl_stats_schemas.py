from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class CrawlStatsItem(BaseModel):
    """Base schema for crawl stats with common fields."""

    subscription_name: str
    total_successful: int = Field(
        ge=0, description="Number of successfully crawled articles"
    )
    total_attempted: int = Field(
        ge=0, description="Total number of articles attempted to crawl"
    )
    crawl_date: date = Field(default_factory=date.today)
    notes: Optional[str] = Field(
        None, max_length=1000, description="Additional notes about the crawl"
    )


class CrawlStatsResponse(BaseModel):
    """Response schema for crawl stats."""

    stats: List[CrawlStatsItem]
    total_count: int
