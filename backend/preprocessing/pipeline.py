from backend.db.session import SessionLocal, init_db
from backend.scrapers.scraper_factory import get_scraper


class PreprocessingPipeline:
    """
    """
    def __init__(self, source_config: dict):
        self.source_config = source_config
        self.db = SessionLocal()
        self.scraper = get_scraper(source_config, self.db)



    def run(self):
        init_db()
        for article in self.scraper.run():
            self.db.add(article)
            self.db.commit()
        self.db.close()
