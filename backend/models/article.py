from sqlalchemy import (
    Column, Integer, String, Boolean,
    Date, DateTime, Float, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.db.session import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    title = Column(String, nullable=False)

    # Beziehung zu Artikeln
    articles = relationship("Article", back_populates="source")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, nullable=False)
    is_agency = Column(Boolean, nullable=False)

    # Welchem Artikel der Author zugeordnet ist
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    article = relationship("Article", back_populates="authors")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    uri = Column(String, nullable=False)
    lang = Column(String, nullable=False)
    is_duplicate = Column(Boolean, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)
    date_time_pub = Column(DateTime, nullable=False)
    data_type = Column(String, nullable=False)
    sim = Column(Float, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    image = Column(String, nullable=True)
    event_uri = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    wgt = Column(Float, nullable=True)
    relevance = Column(Float, nullable=True)

    # ForeignKey auf Source
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source = relationship("Source", back_populates="articles")

    # Liste der Authors
    authors = relationship("Author", back_populates="article")
