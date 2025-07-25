import asyncio
import json
from typing import Dict, List, Set, Tuple
from uuid import UUID

from app.core.db import async_session
from app.core.logger import get_logger
from app.models import Match, MatchingRun, SearchProfile
from app.repositories.match_repository import MatchRepository
from app.repositories.matching_run_repository import MatchingRunRepository
from app.repositories.search_profile_repository import SearchProfileRepository
from app.services.article_vector_service import ArticleVectorService


class ArticleMatchingService:
    """
    Service for matching articles based on their content.
    """

    def __init__(self):
        self.article_vector_service = ArticleVectorService()
        self.logger = get_logger(__name__)
        self.weights = {"topic": 0.7, "keyword": 0.3}
        self.topic_score_threshold = 0.45
        self.keyword_score_threshold = 0.1

    async def process_article_matching_for_search_profile(
        self, search_profile_id: UUID, matching_run: MatchingRun
    ):
        """
        Main entry point to process all matching phases and persist matches.
        """
        profile = await self._load_search_profile(search_profile_id)
        self.logger.info(
            f"Processing article matching "
            f"for search profile: {search_profile_id}"
        )

        topic_scores = await self._phase1_topic_matching(profile)
        keyword_scores = await self._phase2_keyword_matching(
            profile, topic_scores
        )
        keyword_averages = self._compute_keyword_averages(keyword_scores)

        final_matches = self._phase3_finalize_matches(
            topic_scores, keyword_averages
        )
        match_payloads = self._build_match_payloads(
            profile, final_matches, keyword_averages
        )

        await self._persist_matches(
            search_profile_id, final_matches, match_payloads, matching_run
        )
        self.logger.info(
            f"Processing completed for search profile {search_profile_id} "
            f"with {len(final_matches)} potential matches"
        )

    async def _load_search_profile(self, profile_id: UUID) -> SearchProfile:
        profile = await SearchProfileRepository.get_search_profile_by_id(
            profile_id
        )
        if not profile:
            raise ValueError(f"Search profile with ID {profile_id} not found.")
        return profile

    async def _phase1_topic_matching(
        self, profile: SearchProfile
    ) -> Dict[UUID, Dict[UUID, float]]:
        """
        Phase 1 - retrieve topic-level similarity scores.
        Returns a map: topic_id -> { article_id: topic_score }
        """
        topic_score_map: Dict[UUID, Dict[UUID, float]] = {}
        for topic in profile.topics:
            keywords = [kw.name for kw in topic.keywords]
            query = f"Topic {topic.name}: " + ", ".join(keywords)
            retrieved = (
                await self.article_vector_service.retrieve_by_similarity(
                    query, self.topic_score_threshold
                )
            )
            topic_score_map[topic.id] = {
                UUID(doc.metadata["id"]): score for doc, score in retrieved
            }
        return topic_score_map

    async def _phase2_keyword_matching(
        self,
        profile: SearchProfile,
        topic_scores: Dict[UUID, Dict[UUID, float]],
    ) -> Dict[UUID, Dict[UUID, Dict[UUID, List[float]]]]:
        """
        Phase 2 - retrieve per-keyword similarity and store raw scores.
        Returns nested map: topic_id -> article_id -> keyword_id -> [scores]
        """
        keyword_score_map: Dict[UUID, Dict[UUID, Dict[UUID, List[float]]]] = {}
        for topic in profile.topics:
            matched = topic_scores.get(topic.id, {})
            keyword_score_map[topic.id] = {
                art_id: {kw.id: [] for kw in topic.keywords}
                for art_id in matched
            }
            for kw in topic.keywords:
                results = (
                    await self.article_vector_service.retrieve_by_similarity(
                        kw.name, self.keyword_score_threshold
                    )
                )
                for doc, score in results:
                    art_id = UUID(doc.metadata["id"])
                    if art_id in matched:
                        keyword_score_map[topic.id][art_id][kw.id].append(
                            score
                        )
        return keyword_score_map

    def _compute_keyword_averages(
        self,
        keyword_scores: Dict[UUID, Dict[UUID, Dict[UUID, List[float]]]],
    ) -> Dict[UUID, Dict[UUID, float]]:
        """
        Compute average score per article across all keywords of each topic.
        Returns map: topic_id -> article_id -> average_keyword_score
        """
        averages: Dict[UUID, Dict[UUID, float]] = {}
        for topic_id, articles in keyword_scores.items():
            averages[topic_id] = {}
            for art_id, kw_map in articles.items():
                scores = [sum(v) / len(v) for v in kw_map.values() if v]
                averages[topic_id][art_id] = (
                    sum(scores) / len(scores) if scores else 0.0
                )
        return averages

    def _phase3_finalize_matches(
        self,
        topic_scores: Dict[UUID, Dict[UUID, float]],
        keyword_averages: Dict[UUID, Dict[UUID, float]],
    ) -> List[Tuple[UUID, UUID, float]]:
        """
        Combine topic and keyword scores, sort, and dedupe articles.
        Returns list of tuples: (article_id, topic_id, combined_score)
        """
        entries: List[Tuple[UUID, UUID, float]] = []
        for topic_id, arts in topic_scores.items():
            for art_id, t_score in arts.items():
                k_score = keyword_averages.get(topic_id, {}).get(art_id, 0.0)
                total = (
                    t_score * self.weights["topic"]
                    + k_score * self.weights["keyword"]
                )
                entries.append((art_id, topic_id, total))
        entries.sort(key=lambda x: x[2], reverse=True)
        final: List[Tuple[UUID, UUID, float]] = []
        seen: Set[UUID] = set()
        for art_id, topic_id, score in entries:
            if art_id not in seen:
                seen.add(art_id)
                final.append((art_id, topic_id, score))
        return final

    def _build_match_payloads(
        self,
        profile: SearchProfile,
        matches: List[Tuple[UUID, UUID, float]],
        keyword_averages: Dict[UUID, Dict[UUID, float]],
    ) -> List[Dict]:
        """
        Build structured results for logging and storage.
        """
        topic_map = {t.id: t for t in profile.topics}
        results = []
        for art_id, topic_id, combined in matches:
            topic = topic_map[topic_id]
            kws = []
            for kw in topic.keywords:
                kw_score = keyword_averages.get(topic_id, {}).get(art_id, 0.0)
                kws.append(
                    {
                        "keyword_id": kw.id,
                        "keyword_name": kw.name,
                        "score": kw_score,
                    }
                )
            results.append(
                {
                    "article_id": art_id,
                    "topics": [
                        {
                            "topic_id": topic_id,
                            "topic_name": topic.name,
                            "score": combined,
                            "keywords": kws,
                        }
                    ],
                }
            )
        return results

    async def _persist_matches(
        self,
        profile_id: UUID,
        matches: List[Tuple[UUID, UUID, float]],
        results: List[Dict],
        matching_run: MatchingRun,
    ):
        """
        Insert new ones in sorted order,
        but skip articles that are already matched
        to this profile.
        """
        async with async_session() as session:
            inserted_count = 0
            skipped_count = 0

            for _, (art_id, topic_id, score) in enumerate(matches):
                # Check if match already exists for this profile and article
                self.logger.debug(
                    f"Checking if match exists for profile {profile_id} "
                    f"and article {art_id}"
                )
                try:
                    if await MatchRepository.match_exists(
                        session, profile_id, art_id
                    ):
                        skipped_count += 1
                        self.logger.debug(
                            f"Skipping article {art_id} for "
                            f"profile {profile_id} - match already exists"
                        )
                        continue

                    self.logger.debug(
                        f"Inserting match for profile {profile_id} "
                        f"and article {art_id}"
                    )
                    entry = next(
                        r for r in results if r["article_id"] == art_id
                    )
                    match = Match(
                        article_id=art_id,
                        search_profile_id=profile_id,
                        topic_id=topic_id,
                        sorting_order=inserted_count,
                        comment=json.dumps(entry, default=str),
                        score=score,
                        matching_run_id=matching_run.id,
                    )

                    await MatchRepository.insert_match(match, session)
                    inserted_count += 1
                except Exception as e:
                    self.logger.error(
                        f"Error inserting match for profile {profile_id} "
                        f"and article {art_id}: {e}"
                    )
                    continue

            self.logger.info(
                f"Profile {profile_id}: "
                f"Inserted {inserted_count} new matches, "
                f"skipped {skipped_count} existing matches"
            )

    async def run(self, batch_size: int = 100) -> None:
        """
        Run the article matching process in pages,
        processing each profile in parallel.

        :param batch_size: Maximum number of profiles per batch.
        """
        self.logger.info("Starting article matching process")

        offset = 0

        # Initial fetch outside the loop
        profiles: List[SearchProfile] = (
            await SearchProfileRepository.fetch_all_search_profiles(
                limit=batch_size, offset=offset
            )
        )

        matching_run: MatchingRun

        if len(profiles) > 0:
            # Create a matching run entry
            algorithm_version = (
                f"V1_TOPIC_WEIGHTS_{self.weights['topic']}_"
                f"KEYWORD_WEIGHTS_{self.weights['keyword']}"
            )
            async with async_session() as session:
                matching_run = await MatchingRunRepository.create_matching_run(
                    session, algorithm_version=algorithm_version
                )

        # Continue while there are profiles
        while len(profiles) > 0:
            self.logger.info(
                "Fetched %d profiles (offset=%d). Launching tasks...",
                len(profiles),
                offset,
            )

            tasks = [
                asyncio.create_task(
                    self.process_article_matching_for_search_profile(
                        profile.id, matching_run
                    )
                )
                for profile in profiles
            ]
            await asyncio.gather(*tasks)

            offset += batch_size
            profiles = await SearchProfileRepository.fetch_all_search_profiles(
                limit=batch_size, offset=offset
            )

        self.logger.info("Article matching process completed")
