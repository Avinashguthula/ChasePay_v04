from supabase import create_client, Client, ClientOptions
from backend.core.config import settings
import time
import socket

# Cache singleton clients to avoid DNS lookups on every request
_supabase_admin: Client = None
_supabase_anon: Client = None

def _wait_for_dns(host: str, retries: int = 5, delay: float = 1.5):
    """Wait until the hostname resolves, retrying on failure."""
    for i in range(retries):
        try:
            socket.getaddrinfo(host, 443)
            return True
        except socket.gaierror:
            if i < retries - 1:
                print(f"[DNS] Waiting for {host} to resolve (attempt {i+1}/{retries})...")
                time.sleep(delay)
    return False

def _get_supabase_host() -> str:
    """Extract the hostname from the Supabase URL."""
    url = settings.SUPABASE_URL
    return url.replace("https://", "").replace("http://", "").split("/")[0]

def get_admin_client() -> Client:
    """Return a cached admin Supabase client (singleton)."""
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_admin

def get_supabase_client(token: str = None) -> Client:
    """Return a cached anon Supabase client, or a token-based client if token is provided."""
    global _supabase_anon
    if token:
        options = ClientOptions(headers={"Authorization": f"Bearer {token}"})
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY, options=options)
    if _supabase_anon is None:
        _supabase_anon = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _supabase_anon

def call_with_retry(fn, retries: int = 3, delay: float = 1.0):
    """
    Call a Supabase function with automatic retry on DNS/connection failures.
    Usage: result = call_with_retry(lambda: supabase.auth.sign_in_with_password(...))
    """
    host = _get_supabase_host()
    last_error = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            err_str = str(e)
            if "getaddrinfo" in err_str or "11001" in err_str or "Connection" in err_str:
                last_error = e
                print(f"[Supabase] Connection error (attempt {attempt+1}/{retries}): {err_str}")
                # Wait for DNS to resolve before retrying
                _wait_for_dns(host, retries=2, delay=1.0)
                time.sleep(delay)
            else:
                raise  # Non-connection errors bubble up immediately
    raise last_error

# Service role client for backend operations (kept for backward compatibility)
supabase_admin: Client = get_admin_client()
