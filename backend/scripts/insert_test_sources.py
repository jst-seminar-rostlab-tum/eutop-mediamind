# backend/scripts/insert_test_sources.py

from backend.db.session import SessionLocal, init_db
from backend.models.source import NewspaperSource


def insert_test_sources():
    # Tabellen erzeugen, falls noch nicht vorhanden
    init_db()
    db = SessionLocal()

    # Drei Beispiel-Einträge
    test_sources = [
        NewspaperSource(
            title="Frankfurter Allgemeine",
            url="faz.net",
            scraper_type="news_api_ai_scraper",
            config=None,
            login_required=False,
        ),
        NewspaperSource(
            title="Spiegel Online",
            url="spiegel.de",
            scraper_type="news_api_ai_scraper",
            config=None,
            login_required=False,
        )
    ]

    db.add_all(test_sources)
    db.commit()
    db.close()
    print("Zwei Test-Quellen wurden in die Tabelle 'sources' eingefügt.")


if __name__ == "__main__":
    insert_test_sources()
