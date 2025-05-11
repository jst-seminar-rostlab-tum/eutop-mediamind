from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config.settings import Settings

settings = Settings()

# Engine für SQLite, check_same_thread für multithreaded Session
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tabellen automatisch anlegen
def init_db():
    import backend.models.article  # noqa: F401
    import backend.models.source   # noqa: F401
    Base.metadata.create_all(bind=engine)