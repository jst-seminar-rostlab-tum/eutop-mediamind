from config import Configs
from supabase import Client, create_client


def get_supabase_client(cfg: Configs) -> Client:
    if not cfg.SUPABASE_URL or not cfg.SUPABASE_KEY:
        raise Exception(
            status_code=500, detail="Supabase credentials are not set"
        )
    try:
        supabase: Client = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)
        return supabase
    except Exception as e:
        raise Exception(
            status_code=500,
            detail=f"Failed to initialize Supabase client: {str(e)}",
        )
