from typing import Optional
from uuid import UUID

from litellm.batches.main import retrieve_batch

from app.models import SearchProfile
from app.repositories.search_profile_repository import get_search_profile_by_id
from app.services.article_vector_service import ArticleVectorService


class ArticleMatchingService:
    """
    Service for matching articles based on their content.
    """

    def __init__(self):
        self.article_vector_service: ArticleVectorService = (
            ArticleVectorService()
        )  # TODO: Inject this with a methode in an nother brache

    async def process_matching_for_search_profile(
        self, search_profile_id: UUID
    ):
        """
        Process article matching for a given search profile.

        :param search_profile_id: The ID of the search profile to process.
        """
        search_profile: Optional[SearchProfile] = (
            await get_search_profile_by_id(search_profile_id, None)
        )

        if not search_profile:
            raise ValueError(
                f"Search profile with ID {search_profile_id} not found."
            )

        print(search_profile)  # TODO: Remove this line in production

        search_profile_topic_matches = {}

        # Phase 1- Topic Matching
        for topic in search_profile.topics:
            print(
                f"Processing topic: {topic.name}"
            )  # TODO: Remove this line in production
            print(topic.keywords)  # TODO: Remove this line in production
            topic_keywords = [keyword.name for keyword in topic.keywords]
            vector_query = f"Topic {topic.name}: {",".join(topic_keywords)}"
            print(
                f"Vector query: {vector_query}"
            )  # TODO: Remove this line in production
            score_threshold = 0.3  # TODO: Test with is the best value for this
            retrieved_docs = (
                await self.article_vector_service.retrieve_by_similarity(
                    vector_query, score_threshold
                )
            )
            # print(retrieved_docs)  # TODO: Remove this line in production
            search_profile_topic_matches.update(
                {
                    str(topic.id): [
                        (doc.metadata["id"], score)
                        for (doc, score) in retrieved_docs
                    ],
                }
            )

        print(
            search_profile_topic_matches
        )  # TODO: Remove this line in production

        # Phase 2 - Keyword Matching
        for topic in search_profile.topics:
            for keyword in topic.keywords:
                print(f"Processing keyword: {keyword.name}")
                query = keyword.name
                ids = [
                    id
                    for (id, score) in search_profile_topic_matches[
                        str(topic.id)
                    ]
                ]
                print(ids)
                test = (
                    await self.article_vector_service.retrieve_by_similarity(
                        query, score_threshold=0.1
                    )
                )
                print(test)
                retrieved_docs = await self.article_vector_service.retrieve_by_similarity_with_filter(
                    query, ids, score_threshold=0.1
                )
                print(retrieved_docs)

    async def run(self):
        """
        Run the article matching process.
        This method should implement the logic to match articles based on their content.
        """
        # Placeholder for matching logic
        # This could involve comparing article content, keywords, or other attributes
        pass
