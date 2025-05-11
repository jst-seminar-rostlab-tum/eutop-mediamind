from backend.db.session import SessionLocal, init_db
from backend.models.source import NewspaperSource
from backend.preprocessing.pipeline import PreprocessingPipeline


def main():
    init_db()
    db = SessionLocal()
    sources = db.query(NewspaperSource).all()
    print(sources)
    for s in sources:
        cfg = {
            "title": s.title,
            "url": s.url,
            "scraper_type": s.scraper_type,
        }
        pipeline = PreprocessingPipeline(cfg)
        pipeline.run()
    db.close()

if __name__ == "__main__":
    main()