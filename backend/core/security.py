from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.config import settings
from backend.db.supabase import get_supabase_client

security = HTTPBearer()

async def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)):
    token = auth.credentials
    supabase = get_supabase_client()
    try:
        # Verify the token with Supabase directly
        response = supabase.auth.get_user(token)
        user = response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Fetch the user profile from public.users to get the plan
        from backend.db.supabase import supabase_admin
        profile = supabase_admin.table("users").select("*").eq("id", user.id).single().execute()
        
        return {
            "id": user.id,
            "email": user.email,
            "token": token,
            "plan": profile.data.get("plan", "free") if profile.data else "free",
            "gmail_connected": profile.data.get("gmail_connected", False) if profile.data else False
        }
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Auth error: {error_msg}")
        
        # Prevent accidental logouts on network or rate limit errors
        if any(x in error_msg for x in ["getaddrinfo", "network", "connection", "timeout"]):
            raise HTTPException(status_code=503, detail="Auth server unreachable. Please try again.")
        if any(x in error_msg for x in ["rate limit", "too many requests", "429"]):
            raise HTTPException(status_code=429, detail="Too many requests. Please try again.")
            
        raise HTTPException(status_code=401, detail="Could not validate credentials")
