# This file contains the NewsItem dataclass for the PDF service.
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

@dataclass
class NewsItem:
    id: UUID
    title: str
    content: str
    url: str
    published_at: str
    summary: str
    subscription_id: str
    author: Optional[str] = None
    language: Optional[str] = None
    category: Optional[str] = None
    newspaper: Optional[str] = None
    keywords: Optional[list[str]] = None
    image_url: Optional[str] = None
    people: Optional[list] = None
    companies: Optional[list] = None
    politicians: Optional[list] = None
    industries: Optional[list] = None
    legislations: Optional[list] = None
