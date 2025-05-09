import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Load env variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception(
            status_code=500, detail="Supabase credentials are not set"
        )
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        raise Exception(
            status_code=500,
            detail=f"Failed to initialize Supabase client: {str(e)}",
        )
