# This file contains the NewsItem dataclass for the PDF service.
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class NewsItem:
    id: UUID
    title: str
    title_original: str
    content: str
    content_original: str
    url: str
    published_at: str
    summary: str
    subscription_id: UUID
    author: Optional[str] = None
    language: Optional[str] = None
    category: Optional[str] = None
    newspaper: Optional[str] = None
    keywords: Optional[List[str]] = None
    image_url: Optional[str] = None
    persons: Optional[List] = None
    organizations: Optional[List] = None
    industries: Optional[List] = None
    events: Optional[List] = None
    citations: Optional[List] = None
    match: Optional[dict] = None
