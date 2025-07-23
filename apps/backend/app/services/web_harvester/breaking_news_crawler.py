# flake8: noqa
import json
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

                # Detect available languages for title/summary
                # and build headline/summary dicts
                headline = {}
                summary_dict = {}
                language = None
                # Map eventregistry language codes to ISO
                lang_map = {"eng": "en", "deu": "de"}
                for lang_code, text in (titles or {}).items():
                    iso_lang = lang_map.get(lang_code)
                    if iso_lang:
                        headline[iso_lang] = text
                        if language is None:
                            language = iso_lang  # Use first available as main language
                for lang_code, text in (summaries or {}).items():
                    iso_lang = lang_map.get(lang_code)
                    if iso_lang:
                        summary_dict[iso_lang] = text
                relevance_score = event.get("breakingScore", 0.0)
                # The API does not return datetime published_at
                breaking_news = BreakingNews(
                    id=event.get("uri"),
                    headline=headline or None,
                    summary=summary_dict or None,
                    image_url=image,
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
            # Translate headline and summary to both EN and DE if not present
            try:
                # Ensure headline/summary dicts exist
                if not article.headline:
                    article.headline = {}
                if not article.summary:
                    article.summary = {}

                # Translate to English if missing
                if "en" not in article.headline or "en" not in article.summary:
                    translation_en = await ArticleTranslationService.translate_breaking_news_fields(
                        article, Language.EN.value
                    )
                    if translation_en.get("headline"):
                        article.headline["en"] = translation_en["headline"]
                    if translation_en.get("summary"):
                        article.summary["en"] = translation_en["summary"]

                # Translate to German if missing
                if "de" not in article.headline or "de" not in article.summary:
                    translation_de = await ArticleTranslationService.translate_breaking_news_fields(
                        article, Language.DE.value
                    )
                    if translation_de.get("headline"):
                        article.headline["de"] = translation_de["headline"]
                    if translation_de.get("summary"):
                        article.summary["de"] = translation_de["summary"]

                # Send emails if high relevance
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
                        # Use already translated text for email
                        headline_str = article.headline.get(
                            user_language,
                            next(iter(article.headline.values()), ""),
                        )
                        summary_str = article.summary.get(
                            user_language,
                            next(iter(article.summary.values()), ""),
                        )
                        # Build a temporary article object for email content
                        email_article = article.model_copy()
                        # Set headline and summary as strings for email content
                        email_article.headline = headline_str
                        email_article.summary = summary_str
                        email_content = (
                            EmailService._build_breaking_news_email_content(
                                news=email_article, language=user_language
                            )
                        )
                        subject_prefix = (
                            "Breaking News Alert"
                            if user_language == Language.EN.value
                            else "Nachrichten-Alarm"
                        )
                        subject = f"{subject_prefix}: {headline_str}"
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
                    f"Failed to send email and store article {article.id} in Redis: {e}"
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

    async def main():
        print("Fetching breaking news...")
        articles = await fetch_breaking_news_newsapi()
        print(f"Fetched and stored {len(articles)} breaking news articles.")
        for article in articles:
            print(f"ID: {article.id}")
            print(f"Headline: {article.headline}")
            print(f"Summary: {article.summary}")
            print(f"Relevance: {article.relevance_score}")
            print(f"Language: {article.language}")
            print("---")

    asyncio.run(main())
