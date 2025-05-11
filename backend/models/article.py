from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import date, datetime


class Author(BaseModel):
    uri: str
    isAgency: bool


class Source(BaseModel):
    uri: str
    dataType: str
    title: str


class Article(BaseModel):
    uri: str
    lang: str
    isDuplicate: bool
    date: date
    time: str
    dateTime: datetime
    dateTimePub: datetime = Field(..., alias="dateTimePub")
    dataType: str
    sim: float
    url: HttpUrl
    title: str
    body: str
    source: Source
    authors: List[Author]
    image: Optional[HttpUrl]
    eventUri: Optional[str]
    sentiment: Optional[str]
    wgt: Optional[float]
    relevance: Optional[float]

    class Config:
        validate_by_name = True
        extra = "ignore"