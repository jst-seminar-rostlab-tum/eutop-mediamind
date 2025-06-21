from typing import Optional, Dict, List, Tuple, Set
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

        # Phase 1- Topic Matching

        topic_score_map: Dict[UUID, Dict[UUID, float]] = {}
        topic_score_threshold = 0.3

        for topic in search_profile.topics:
            print(
                f"Processing topic: {topic.name}"
            )  # TODO: Remove this line in production
            # Build a vector query from the topic name and its keywords
            keyword_names = [kw.name for kw in topic.keywords]
            vector_query = f"Topic {topic.name}: " + ", ".join(keyword_names)

            print(
                f"Vector query: {vector_query}"
            )  # TODO: Remove this line in production
            # Retrieve similar articles above the threshold
            retrieved = (
                await self.article_vector_service.retrieve_by_similarity(
                    vector_query, topic_score_threshold
                )
            )
            # print(retrieved_docs)  # TODO: Remove this line in production
            # Map article_id -> topic_score
            topic_score_map[topic.id] = {
                UUID(doc.metadata["id"]): score for doc, score in retrieved
            }

        print(topic_score_map)  # TODO: Remove this line in production

        # Phase 2 - Keyword Matching

        keyword_score_map: Dict[UUID, Dict[UUID, List[float]]] = {}
        keyword_score_threshold = 0.1

        for topic in search_profile.topics:
            keyword_score_map[topic.id] = {}
            matched_articles = topic_score_map.get(topic.id, {})

            for keyword in topic.keywords:
                print(f"Processing keyword: {keyword.name}")
                # Retrieve articles similar to the single keyword
                retrieved = (
                    await self.article_vector_service.retrieve_by_similarity(
                        keyword.name, keyword_score_threshold
                    )
                )

                for doc, score in retrieved:
                    art_id = UUID(doc.metadata["id"])
                    # Only consider articles already matched in Phase 1
                    if art_id in matched_articles:
                        print("Found matching article:", art_id)
                        keyword_score_map[topic.id].setdefault(
                            art_id, []
                        ).append(score)

        ## Compute average keyword score per article
        keyword_avg_score_map: Dict[UUID, Dict[UUID, float]] = {}
        for topic_id, scores_by_article in keyword_score_map.items():
            keyword_avg_score_map[topic_id] = {
                art_id: sum(scores) / len(scores)
                for art_id, scores in scores_by_article.items()
            }

        # Phase 3 - Finalizing Matches

        weights = {"topic": 0.7, "keyword": 0.3}
        score_entries: List[Tuple[UUID, UUID, float]] = []

        for topic_id, articles in topic_score_map.items():
            for art_id, t_score in articles.items():
                k_score = keyword_avg_score_map.get(topic_id, {}).get(
                    art_id, 0.0
                )
                total_score = (
                    t_score * weights["topic"] + k_score * weights["keyword"]
                )
                score_entries.append((art_id, topic_id, total_score))

        score_entries.sort(key=lambda x: x[2], reverse=True)

        final_matches: List[Tuple[UUID, UUID, float]] = []
        seen_article_ids: Set[UUID] = set()

        for art_id, topic_id, score in score_entries:
            if art_id not in seen_article_ids:
                seen_article_ids.add(art_id)
                final_matches.append((art_id, topic_id, score))

        # TODO: print list of (article_id, topic_id, score) tuples sorted by score

        print(final_matches)

    async def run(self):
        """
        Run the article matching process.
        This method should implement the logic to match articles based on their content.
        """
        # Placeholder for matching logic
        # This could involve comparing article content, keywords, or other attributes
        pass
