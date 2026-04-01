from config import Config
from supabase import create_client, Client

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
def get_supabase_client() -> Client:
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        raise ValueError("Missing Supabase configuration")
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)