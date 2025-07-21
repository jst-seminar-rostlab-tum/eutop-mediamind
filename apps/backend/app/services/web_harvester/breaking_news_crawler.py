import json
import uuid
from datetime import date as Date
from datetime import datetime, timedelta, timezone
from typing import List

import requests
from eventregistry import EventRegistry

from app.core.config import get_configs
from app.core.db import get_redis_connection
from app.core.languages import Language
from app.core.logger import BufferedLogger
from app.models.breaking_news import BreakingNews
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.services.translation_service import ArticleTranslationService

configs = get_configs()


class BreakingNewsNewsAPICrawler:
    """
    NewsAPICrawler for breaking news articles.
    This crawler is independent of the Subscription model
    and is used to fetch breaking news articles from the NewsAPI.ai service.
    """

    def __init__(self):
        self.logger = BufferedLogger("BreakingNewsNewsAPICrawler")
        if not configs.NEWSAPIAI_API_KEY:
            self.logger.error(
                "NEWSAPIAI_API_KEY is not set in the configuration."
            )
            raise ValueError(
                "NEWSAPIAI_API_KEY is not set in the configuration."
            )

        try:
            self.er = EventRegistry(apiKey=configs.NEWSAPIAI_API_KEY)
        except Exception as e:
            self.logger.error(f"Failed to initialize EventRegistry: {e}")
            raise

        self.url = "https://eventregistry.org/api/v1/event/getEvents"
        self.event_detail_url = (
            "https://eventregistry.org/api/v1/event/getEvent"
        )
        self.logger.info("NewsAPICrawler initialized with API key.")

    def fetch_breaking_news(
        self,
    ) -> List[BreakingNews]:
        """
        Fetches breaking news articles from the NewsAPI.ai service.
        :return: A list of Article objects containing breaking news articles.
        """
        query = self.build_query()

        headers = {"Content-Type": "application/json"}
        try:
            # Manual request to the NewsAPI.ai API because the EventRegistry
            # does not support breaking news queries directly.
            response = requests.post(self.url, json=query, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data.get("breakingEvents"):
                self.logger.info("No breaking news found.")
                return []

            breaking_news_list = []
            for event in data["breakingEvents"]["results"]:
                image = event.get("images")[0] if event.get("images") else None

                titles = event.get("title")
                summaries = event.get("summary")

                # Detect language for title/summary
                if "eng" in titles:
                    title = titles["eng"]
                    language = "en"
                elif "deu" in titles:
                    title = titles["deu"]
                    language = "de"
                else:
                    title = None
                    language = None

                if "eng" in summaries:
                    summary = summaries["eng"]
                elif "deu" in summaries:
                    summary = summaries["deu"]
                else:
                    summary = None

                relevance_score = event.get("breakingScore", 0.0)
                # The API does not return datetime published_at
                breaking_news = BreakingNews(
                    id=event.get("uri"),
                    title=title,
                    image_url=image,
                    summary=summary,
                    relevance_score=relevance_score,
                    language=language,
                )
                breaking_news_list.append(breaking_news)

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch breaking news: {e}")
            return []

        return breaking_news_list

    def build_query(
        self,
        date_start: Date = Date.today() - timedelta(days=1),
        date_end: Date = Date.today(),
    ):
        """
        Builds the query for the EventRegistry API.
        """

        news_categories = [
            {"categoryUri": "news/Business"},
            {"categoryUri": "news/Health"},
            {"categoryUri": "news/Politics"},
            {"categoryUri": "news/Science"},
            {"categoryUri": "news/Environment"},
            {"categoryUri": "news/Technology"},
        ]

        location_uris = [
            {"locationUri": "http://en.wikipedia.org/wiki/European_Union"},
            {"locationUri": "http://en.wikipedia.org/wiki/United_Kingdom"},
            {"locationUri": "http://en.wikipedia.org/wiki/Switzerland"},
            {"locationUri": "http://en.wikipedia.org/wiki/United_States"},
            {"locationUri": "http://en.wikipedia.org/wiki/Canada"},
        ]

        language_uris = [{"lang": "eng"}, {"lang": "deu"}]

        query_conditions = [
            {"$or": news_categories},
            {"$or": location_uris},
            {"$or": language_uris},
            {
                "dateStart": date_start.strftime("%Y-%m-%d"),
                "dateEnd": date_end.strftime("%Y-%m-%d"),
            },
        ]

        query = {
            "query": {"$query": {"$and": query_conditions}},
            "resultType": "breakingEvents",
            "breakingEventsSortBy": "rel",
            "eventImageCount": 1,
            "storyImageCount": 1,
            "includeStoryDate": True,
            "apiKey": configs.NEWSAPIAI_API_KEY,
        }

        return query

    def get_breaking_news_detail(
        self, breaking_news: BreakingNews
    ) -> BreakingNews:
        """
        Fetches detailed information about a specific breaking news event.
        :param event_id: The ID of the breaking news event.
        :return: A BreakingNews object with detailed information.
        """

        query = {
            "eventUri": [breaking_news.id],
            "resultType": "articles",
            "articlesSortBy": "sim",
            "apiKey": configs.NEWSAPIAI_API_KEY,
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self.event_detail_url, json=query, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            data = data.get(breaking_news.id)
            if not data.get("articles") or not data.get("articles").get(
                "results"
            ):
                self.logger.info(
                    f"No articles found for event {breaking_news.id}."
                )
                return None

            results = data.get("articles").get("results")
            results.sort(key=lambda x: x.get("sim", 0), reverse=True)

            best_match_article = results[0]

            date_str = best_match_article.get("dateTimePub")
            if date_str:
                date = datetime.strptime(
                    date_str, "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)
                breaking_news.published_at = date.isoformat()

            breaking_news.url = best_match_article.get("url")

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch breaking news detail: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing breaking news detail: {e}")
            return None

        return breaking_news


async def fetch_breaking_news_newsapi():
    """
    Fetches breaking news articles using the BreakingNewsNewsAPICrawler.
    Stores each article in Redis individually, skipping duplicates based on ID.

    :return: A list of BreakingNews objects that were successfully stored in
    Redis.
    """
    crawler = BreakingNewsNewsAPICrawler()
    new_articles = crawler.fetch_breaking_news()
    redis_engine = get_redis_connection()
    stored_articles = []

    for article in new_articles:
        redis_key = f"breaking_news:{article.id}"
        if not redis_engine.exists(redis_key):
            article = crawler.get_breaking_news_detail(article)
            if not article:
                continue  # Newsapi sometimes returns empty articles
            try:
                # if the article has high relevance score, send emails
                if article.relevance_score > 0.8:
                    crawler.logger.info(
                        f"Sending breaking news alert for article {article.id}"
                    )

                    users = await UserRepository.get_all_users_breaking_news()
                    for user in users:
                        user_language = (
                            user.language
                            if hasattr(user, "language")
                            else Language.EN.value
                        )

                        if (
                            user_language == Language.DE.value
                            and article.language != Language.DE.value
                        ):
                            crawler.logger.info(
                                f"Translating article {article.id} to German"
                            )
                            translation = await ArticleTranslationService.translate_breaking_news_fields(
                                article, Language.DE.value
                            )
                            article = article.__class__(
                                **{
                                    **article.model_dump(),
                                    **translation,
                                    "language": Language.DE.value,
                                }
                            )
                        elif (
                            user_language == Language.EN.value
                            and article.language != Language.EN.value
                        ):
                            crawler.logger.info(
                                f"Translating article {article.id} to English"
                            )
                            translation = await ArticleTranslationService.translate_breaking_news_fields(
                                article, Language.EN.value
                            )
                            article = article.__class__(
                                **{
                                    **article.model_dump(),
                                    **translation,
                                    "language": Language.EN.value,
                                }
                            )

                        email_content = (
                            EmailService._build_breaking_news_email_content(
                                news=article, language=user_language
                            )
                        )

                        subject_prefix = (
                            "Breaking News Alert"
                            if user_language == Language.EN.value
                            else "Nachrichten-Alarm"
                        )
                        subject = f"{subject_prefix}: {article.title}"

                        email = EmailService.create_email(
                            recipient=user.email,
                            subject=subject,
                            content_type="text/plain",
                            content=email_content,
                        )
                        await EmailService.send_email(email=email)

                # Store the article in Redis
                redis_engine.set(
                    redis_key,
                    json.dumps(article.model_dump()),
                    ex=86400,  # 1 day expiration
                )
                stored_articles.append(article)
                crawler.logger.info(f"Stored article {article.id} in Redis.")
            except Exception as e:
                crawler.logger.error(
                    f"Failed to store article {article.id} in Redis: {e}"
                )

    crawler.logger.flush()
    return stored_articles


def get_all_breaking_news() -> List[BreakingNews]:
    """
    Retrieves all breaking news articles stored in Redis under keys matching
    'breaking_news:*'.
    :return: List of BreakingNews objects.
    """
    try:
        redis_engine = get_redis_connection()

        keys = redis_engine.keys("breaking_news:*")
        articles = []

        for key in keys:
            raw_data = redis_engine.get(key)
            if raw_data:
                data = json.loads(raw_data)
                article = BreakingNews(**data)
                articles.append(article)

        return articles

    except Exception as e:
        logger = BufferedLogger("BreakingNewsRedisReader")
        logger.error(f"Failed to fetch breaking news from Redis: {e}")
        return []


if __name__ == "__main__":
    import asyncio

    # Fetch and store breaking news in Redis
    stored_articles = asyncio.run(fetch_breaking_news_newsapi())
