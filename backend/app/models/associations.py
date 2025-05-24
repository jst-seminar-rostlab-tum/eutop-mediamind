import uuid

from sqlmodel import Field, SQLModel


class TopicKeywordLink(SQLModel, table=True):
    __tablename__ = "topics_keywords"

    topic_id: uuid.UUID = Field(
        foreign_key="topics.id", nullable=False, primary_key=True
    )
    keyword_id: uuid.UUID = Field(
        foreign_key="keywords.id", nullable=False, primary_key=True
    )


class OrganizationSubscriptionLink(SQLModel, table=True):
    __tablename__ = "organizations_subscriptions"

    organization_id: uuid.UUID = Field(
        foreign_key="organizations.id", nullable=False, primary_key=True
    )
    subscription_id: uuid.UUID = Field(
        foreign_key="subscriptions.id", nullable=False, primary_key=True
    )


class ArticleKeywordLink(SQLModel, table=True):
    __tablename__ = "articles_keywords"

    article_id: uuid.UUID = Field(
        foreign_key="articles.id", nullable=False, primary_key=True
    )
    keyword_id: uuid.UUID = Field(
        foreign_key="keywords.id", nullable=False, primary_key=True
    )
    score: float


class SearchProfileSubscriptionLink(SQLModel, table=True):
    __tablename__ = "search_profiles_subscriptions"

    search_profile_id: uuid.UUID = Field(
        foreign_key="search_profiles.id", nullable=False, primary_key=True
    )
    subscription_id: uuid.UUID = Field(
        foreign_key="subscriptions.id", nullable=False, primary_key=True
    )


class UserSearchProfileLink(SQLModel, table=True):
    __tablename__ = "users_search_profiles"

    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, primary_key=True
    )
    search_profile_id: uuid.UUID = Field(
        foreign_key="search_profiles.id", nullable=False, primary_key=True
    )
