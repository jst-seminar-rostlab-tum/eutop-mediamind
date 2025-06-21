import json
from datetime import date
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from app.models import Match, SearchProfile
from app.repositories.match_repository import MatchRepository
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

        # Phase 1 - Topic Matching
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
            # Map article_id -> topic_score
            topic_score_map[topic.id] = {
                UUID(doc.metadata["id"]): score for doc, score in retrieved
            }

        print(topic_score_map)  # TODO: Remove this line in production

        # Phase 2 - Keyword Matching
        # Track scores per keyword per article
        keyword_score_map: Dict[UUID, Dict[UUID, Dict[UUID, List[float]]]] = {}
        keyword_score_threshold = 0.1

        for topic in search_profile.topics:
            matched_articles = topic_score_map.get(topic.id, {})
            # Initialize nested structure: article_id -> { keyword_id: [] }
            keyword_score_map[topic.id] = {
                art_id: {kw.id: [] for kw in topic.keywords}
                for art_id in matched_articles
            }

            for keyword in topic.keywords:
                print(
                    f"Processing keyword: {keyword.name}"
                )  # TODO: Remove this line in production
                retrieved = (
                    await self.article_vector_service.retrieve_by_similarity(
                        keyword.name, keyword_score_threshold
                    )
                )

                for doc, score in retrieved:
                    art_id = UUID(doc.metadata["id"])
                    # Only consider articles already matched in Phase 1
                    if art_id in matched_articles:
                        print(
                            "Found matching article:", art_id
                        )  # TODO: Remove in production
                        # Record score for this specific keyword
                        keyword_score_map[topic.id][art_id][keyword.id].append(
                            score
                        )

        # Compute average keyword score per keyword per article
        keyword_avg_per_keyword_map: Dict[
            UUID, Dict[UUID, Dict[UUID, float]]
        ] = {}
        for topic_id, art_scores in keyword_score_map.items():
            keyword_avg_per_keyword_map[topic_id] = {}
            for art_id, kw_scores in art_scores.items():
                keyword_avg_per_keyword_map[topic_id][art_id] = {
                    kw_id: (sum(scores) / len(scores)) if scores else 0.0
                    for kw_id, scores in kw_scores.items()
                }

        # Phase 3 - Finalizing Matches
        weights = {"topic": 0.7, "keyword": 0.3}
        score_entries: List[Tuple[UUID, UUID, float]] = []

        for topic_id, articles in topic_score_map.items():
            for art_id, t_score in articles.items():
                # Overall keyword score per article
                k_scores = keyword_avg_per_keyword_map.get(topic_id, {}).get(
                    art_id, {}
                )
                k_score = (
                    (sum(k_scores.values()) / len(k_scores))
                    if k_scores
                    else 0.0
                )
                total_score = (
                    t_score * weights["topic"] + k_score * weights["keyword"]
                )
                score_entries.append((art_id, topic_id, total_score))

        # Sort by descending combined score
        score_entries.sort(key=lambda x: x[2], reverse=True)

        # Remove duplicates: retain only first occurrence per article
        final_matches: List[Tuple[UUID, UUID, float]] = []
        seen_article_ids: Set[UUID] = set()
        for art_id, topic_id, score in score_entries:
            if art_id not in seen_article_ids:
                seen_article_ids.add(art_id)
                final_matches.append((art_id, topic_id, score))

        # Build structured result list based on final_matches
        from collections import defaultdict

        article_topics_map: Dict[UUID, List[Dict]] = defaultdict(list)
        topic_map = {topic.id: topic for topic in search_profile.topics}

        for art_id, topic_id, combined_score in final_matches:
            topic = topic_map[topic_id]
            keywords_list = []
            for keyword in topic.keywords:
                kw_score = (
                    keyword_avg_per_keyword_map.get(topic_id, {})
                    .get(art_id, {})
                    .get(keyword.id, 0.0)
                )
                keywords_list.append(
                    {
                        "keyword_id": keyword.id,
                        "keyword_name": keyword.name,
                        "score": kw_score,
                    }
                )

            article_topics_map[art_id].append(
                {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "score": combined_score,
                    "keywords": keywords_list,
                }
            )

        results: List[Dict] = []
        for art_id, topics in article_topics_map.items():
            results.append(
                {
                    "article_id": art_id,
                    "topics": topics,
                }
            )

        print(
            final_matches
        )  # TODO: Replace with return or other handling in production
        print(
            results
        )  # TODO: Replace with return or other handling in production

        # Persist Matches to the database and attach 'results' as comment
        matches: List[Match] = []
        await MatchRepository.cleanup_matches(search_profile_id, date.today())
        for idx, (art_id, topic_id, score) in enumerate(final_matches):
            # Find the result entry for this article
            result_entry = next(
                r for r in results if r["article_id"] == art_id
            )
            match = Match(
                article_id=art_id,
                search_profile_id=search_profile_id,
                topic_id=topic_id,
                sorting_order=idx,
                comment=json.dumps(
                    result_entry, default=str
                ),  # results soll als comment hinzugefügt werden
                match_date=date.today(),
            )

            await MatchRepository.insert_match(match)
            matches.append(match)

        print(matches)

    async def run(self):
        """
        Run the article matching process.
        """
        # Placeholder for matching logic
        pass
