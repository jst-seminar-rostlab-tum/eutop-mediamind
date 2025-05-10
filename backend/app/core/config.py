import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

class Configs():
    # base
    ENV: str = os.getenv("ENV", "dev")
    PROJECT_NAME: str = "mediamind"

    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # database
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")


configs = Configs()

