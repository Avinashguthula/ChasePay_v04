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
            "plan": profile.data.get("plan", "free") if profile.data else "free"
        }
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
