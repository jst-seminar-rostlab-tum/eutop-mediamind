import os
from dotenv import load_dotenv
from supabase import Client, create_client
from config import Configs


def get_supabase_client(cfg: Configs) -> Client:
    if not cfg.SUPABASE_URL or not cfg.SUPABASE_KEY:
        raise Exception("Supabase credentials are not set")
    try:
        return create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)
    except Exception as e:
        raise Exception(f"Failed to initialize Supabase client: {str(e)}")
