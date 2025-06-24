from typing import List, Optional
from uuid import UUID

from app.core.db import async_session
from app.models.entity import ArticleEntity


class ArticleEntityRepository:

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
                entities.extend([
                    ArticleEntity(
                        article_id=article_id,
                        entity_type="person",
                        value=p
                    )
                    for p in persons
                ])
            if industries:
                entities.extend([
                    ArticleEntity(
                        article_id=article_id,
                        entity_type="industry",
                        value=i
                    )
                    for i in industries
                ])
            if events:
                entities.extend([
                    ArticleEntity(
                        article_id=article_id,
                        entity_type="event",
                        value=e
                    )
                    for e in events
                ])
            if organizations:
                entities.extend([
                    ArticleEntity(
                        article_id=article_id,
                        entity_type="organization",
                        value=o
                    )
                    for o in organizations
                ])

            session.add_all(entities)
            await session.commit()
