from eventregistry import *


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
