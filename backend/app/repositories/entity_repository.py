from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from app.core.db import async_session
from app.models.entity import ArticleEntity


class ArticleEntityRepository:
    """
    This repository manages 'entities' extracted from articles.

    An entity refers to a relevant keyword or named item detected in
    the article's content.
    It can be one of several types, such as:
    - person
    - industry
    - event
    - organization
    """

    @staticmethod
    async def get_entities_by_article(article_id: UUID) -> dict:
        async with async_session() as session:
            result = await session.execute(
                select(ArticleEntity).where(
                    ArticleEntity.article_id == article_id
                )
            )
            entities = result.scalars().all()

            grouped_entities = {
                "person": [],
                "industry": [],
                "event": [],
                "organization": [],
            }
            for entity in entities:
                grouped_entities[entity.entity_type].append(entity.value)

            return grouped_entities

    @staticmethod
    async def add_entities(
        article_id: UUID,
        persons: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        organizations: Optional[List[str]] = None,
    ) -> None:
        async with async_session() as session:
            entities = []
            if persons:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type="person",
                            value=p,
                        )
                        for p in persons
                    ]
                )
            if industries:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type="industry",
                            value=i,
                        )
                        for i in industries
                    ]
                )
            if events:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id, entity_type="event", value=e
                        )
                        for e in events
                    ]
                )
            if organizations:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type="organization",
                            value=o,
                        )
                        for o in organizations
                    ]
                )

            session.add_all(entities)
            await session.commit()
