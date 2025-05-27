import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Configs:
    # base
    ENV: str = os.getenv("ENV", "dev")
    PROJECT_NAME: str = "mediamind"

    PROJECT_ROOT: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL")

    # Configuration of the user management tool (Clerk)
    CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
    CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")


configs = Configs()
