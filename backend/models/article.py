from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Article(BaseModel):
    """
    Data model for news articles used throughout the scraping and preprocessing pipeline.
    """

    title: str = Field(..., description="Headline of the article")
    author: Optional[str] = Field(None, description="Author(s) of the article, if available")
    published_at: Optional[datetime] = Field(
        None, description="Publication date and time of the article"
    )
    source: Optional[str] = Field(None, description="Source or publisher name")
    url: Optional[str] = Field(None, description="Original URL of the article")
    text: str = Field(..., description="Full text or body of the article")
    keywords: List[str] = Field(default_factory=list, description="Query or keywords that matched the article")
    entities: List[str] = Field(default_factory=list, description="Extracted named entities or topics")

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        allow_population_by_field_name = True