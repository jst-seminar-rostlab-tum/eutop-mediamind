import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Supabase credentials are not set")
    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        raise Exception(f"Failed to initialize Supabase client: {str(e)}")
