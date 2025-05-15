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

    # Supabase Auth
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
    SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID", "")
    REDIRECT_URL = os.getenv(
        "SUPABASE_REDIRECT_URL", "http://localhost:8000/api/v1/auth/callback"
    )


configs = Configs()
