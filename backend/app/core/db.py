import psycopg2
from psycopg2 import OperationalError
from psycopg2.extensions import connection as PgConnection

from app.core.config import Configs


def get_postgresql_connection(cfg: Configs) -> PgConnection:
    if not cfg.DATABASE_URL:
        raise ValueError("DATABASE_URL not set in config.")
    try:
        return psycopg2.connect(dsn=cfg.DATABASE_URL)
    except OperationalError as e:
        raise Exception(f"Failed to connect to PostgreSQL database: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to initialize PostgreSQL client: {str(e)}")


def get_domain_to_crawl():
    return ["https://www.bild.de/", "https://www.sueddeutsche.de/"]
