from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select

from app.core.db import async_session
from app.models.entity import ArticleEntity, EntityType


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
    async def get_entities_by_article(
        article_id: UUID, language: str = "en"
    ) -> dict:
        """
        Retrieves the entities associated with a given article,
        int the specified language (if translation does not exist
        uses default value)
        """
        async with async_session() as session:
            result = await session.execute(
                select(ArticleEntity).where(
                    ArticleEntity.article_id == article_id
                )
            )
            entities = result.scalars().all()

            grouped_entities = {e.value: [] for e in EntityType}

            for entity in entities:
                value = (
                    getattr(entity, f"value_{language}", None) or entity.value
                )
                grouped_entities[entity.entity_type].append(value)

            return grouped_entities

    @staticmethod
    async def get_entities_without_translations(
        limit: int = 100, offset: int = 0
    ) -> List[ArticleEntity]:
        async with async_session() as session:
            result = await session.execute(
                select(ArticleEntity)
                .where(
                    and_(
                        ArticleEntity.entity_type.in_(["industry", "event"]),
                        or_(
                            ArticleEntity.value_en.is_(None),
                            ArticleEntity.value_en == "",
                            ArticleEntity.value_de.is_(None),
                            ArticleEntity.value_de == "",
                        ),
                    )
                )
                .limit(limit)
                .offset(offset)
            )
            entities = result.scalars().all()
            return entities

    @staticmethod
    async def update_translations(
        entity_id: UUID,
        value_en: Optional[str] = None,
        value_de: Optional[str] = None,
    ) -> None:
        async with async_session() as session:
            result = await session.execute(
                select(ArticleEntity).where(ArticleEntity.id == entity_id)
            )
            entity = result.scalar_one_or_none()

            if entity is None:
                raise ValueError(f"Entity with ID {entity_id} not found.")

            if value_en is not None:
                entity.value_en = value_en
            if value_de is not None:
                entity.value_de = value_de

            session.add(entity)
            await session.commit()

    @staticmethod
    async def add_entities(
        article_id: UUID,
        persons: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        organizations: Optional[List[str]] = None,
        citations: Optional[List[str]] = None,
    ) -> None:
        async with async_session() as session:
            entities = []
            if persons:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type=EntityType.PERSON,
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
                            entity_type=EntityType.INDUSTRY,
                            value=i,
                        )
                        for i in industries
                    ]
                )
            if events:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type=EntityType.EVENT,
                            value=e,
                        )
                        for e in events
                    ]
                )
            if organizations:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type=EntityType.ORGANIZATION,
                            value=o,
                        )
                        for o in organizations
                    ]
                )
            if citations:
                entities.extend(
                    [
                        ArticleEntity(
                            article_id=article_id,
                            entity_type=EntityType.CITATION,
                            value=c,
                        )
                        for c in citations
                    ]
                )

            session.add_all(entities)
            await session.commit()
