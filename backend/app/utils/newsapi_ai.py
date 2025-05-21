from typing import Any

from eventregistry import *
import requests
from urllib.parse import urlparse


async def get_articles_from_news_api_ai(
    source_uris: list[str], date_start: str, date_end: str
) -> list[dict]:
    er = EventRegistry(apiKey="f3ec0636-e14b-4fe6-980b-fc0720ab8131")

    query = {
        "$query": {
            "$and": [
                {"$or": [{"sourceUri": uri} for uri in source_uris]},
                {
                    "$or": [
                        {"categoryUri": "news/Environment"},
                        {"categoryUri": "news/Business"},
                        {"categoryUri": "news/Health"},
                        {"categoryUri": "news/Politics"},
                        {"categoryUri": "news/Technology"},
                        {"categoryUri": "news/Science"},
                    ]
                },
                {"dateStart": date_start, "dateEnd": date_end},
            ]
        }
    }

    q = QueryArticlesIter.initWithComplexQuery(query)

    articles = []
    for article in q.execQuery(er, maxItems=100):
        articles.append(
            {
                "title": article.get("title"),
                "url": article.get("url"),
                "datetime": article.get("dateTime"),
                "author": article.get("author", None),
            }
        )

    print("Number of articles: ", len(articles))
    for a in articles:
        print(a["title"], a["url"])

    return articles


async def get_breaking_events_from_news_api_ai(
    min_score: float = 0.2,
) -> list[dict]:
    url = "https://eventregistry.org/api/v1/event/getBreakingEvents"
    payload = {
        "breakingEventsMinBreakingScore": min_score,
        "apiKey": "f3ec0636-e14b-4fe6-980b-fc0720ab8131",
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        events = data.get("breakingEvents", {}).get("results", [])
        return events
    else:
        print(
            f"Failed to fetch breaking events: {response.status_code} {response.text}"
        )
        return []


def get_best_matching_source(prefix: str, api_key: str) -> Any | None:
    """
    Überprüft, ob eine Domain in der NewsAPI.ai-Datenbank enthalten ist, und gibt die beste Übereinstimmung zurück.

    Parameter:
        prefix (str): Die zu überprüfende URL.
        api_key (str): Dein NewsAPI.ai API-Schlüssel.

    Rückgabe:
        dict: Die Quelle mit dem höchsten Relevanz-Score, oder None, wenn keine geeignete Quelle gefunden wurde.
    """
    # Extrahiere die Domain aus der URL
    parsed_url = urlparse(prefix)
    domain = parsed_url.netloc

    # Definiere den API-Endpunkt und die Parameter
    url = 'https://newsapi.ai/api/v1/suggestSources'
    params = {
        'text': domain,
        'apiKey': api_key
    }

    try:
        # Führe die API-Anfrage aus
        response = requests.get(url, params=params)
        response.raise_for_status()  # Fehler bei schlechten Statuscodes auslösen

        # Analysiere die JSON-Antwort
        sources = response.json()

        if not sources:
            print("Keine Quellen für das angegebene Präfix gefunden.")
            return None

        # Finde die Quelle mit dem höchsten Score
        best_source = max(sources, key=lambda x: x.get('score', 0))

        # Überprüfe, ob der Score über dem Schwellenwert liegt
        if best_source.get('score', 0) >= 50000:
            return best_source
        else:
            print("Gefundene Quelle hat einen Score unter 50.000. Wird ignoriert.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ein Fehler ist bei der API-Anfrage aufgetreten: {e}")
        return None
