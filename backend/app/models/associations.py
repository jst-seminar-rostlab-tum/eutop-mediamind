# models/associations.py

import uuid
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import UniqueConstraint

class OrganizationSubscription(SQLModel, table=True):
    __tablename__ = "organization_subscriptions"
    __table_args__ = (UniqueConstraint("organization_id", "subscription_id", name="uq_org_sub"),)

    organization_id: uuid.UUID = Field(foreign_key="organizations.id", primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="subscriptions.id", primary_key=True)

    organization = Relationship(back_populates="subscriptions_link")
    subscription = Relationship(back_populates="organizations_link")


class TopicKeyword(SQLModel, table=True):
    __tablename__ = "topic_keywords"
    __table_args__ = (UniqueConstraint("topic_id", "keyword_id", name="uq_topic_keyword"),)

    topic_id: uuid.UUID = Field(foreign_key="topics.id", primary_key=True)
    keyword_id: uuid.UUID = Field(foreign_key="keywords.id", primary_key=True)

    topic = Relationship(back_populates="topics_link")
    keyword = Relationship(back_populates="keywords_link")


class ArticleKeyword(SQLModel, table=True):
    __tablename__ = "article_keywords"
    __table_args__ = (UniqueConstraint("article_id", "keyword_id", name="uq_article_keyword"),)

    article_id: uuid.UUID = Field(foreign_key="articles.id", primary_key=True)
    keyword_id: uuid.UUID = Field(foreign_key="keywords.id", primary_key=True)
    score: float = Field(default=0.0)

    article = Relationship(back_populates="keywords_link")
    keyword = Relationship(back_populates="articles_link")
