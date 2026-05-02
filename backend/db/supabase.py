from supabase import create_client, Client, ClientOptions
from backend.core.config import settings

# Service role client for backend operations
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def get_supabase_client(token: str = None) -> Client:
    if token:
        # Create client with user's JWT using ClientOptions
        options = ClientOptions(headers={"Authorization": f"Bearer {token}"})
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY, options=options)
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
