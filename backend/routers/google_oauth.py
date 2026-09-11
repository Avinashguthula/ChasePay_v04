from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from backend.core.security import get_current_user
from backend.core.config import settings
from backend.db.supabase import supabase_admin
import httpx

router = APIRouter(prefix="/connect/google", tags=["Google OAuth"])

@router.get("/login")
async def google_login(user: dict = Depends(get_current_user)):
    # Generate Google Auth URL
    # For MVP, we'll return the URL the frontend should redirect to

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=https://www.googleapis.com/auth/gmail.send&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={user['id']}"
    )
    return {"url": auth_url}

@router.get("/callback")
async def google_callback(code: str, state: str):
    # state contains the user_id
    user_id = state
    print(f"DEBUG: Google Callback received for User ID: {user_id}")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
        )
        tokens = response.json()
        print(f"DEBUG: Google Token Response: {tokens}")
        
    if "access_token" not in tokens:
        print(f"ERROR: No access_token in Google response: {tokens}")
        raise HTTPException(status_code=400, detail="Failed to get tokens from Google")
        
    # Update user in DB
    supabase_admin.table("users").update({
        "gmail_connected": True,
        "gmail_access_token": tokens.get("access_token"),
        "gmail_refresh_token": tokens.get("refresh_token"),
    }).eq("id", user_id).execute()
    
    # Redirect back to frontend settings
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings?connected=true")

@router.post("/disconnect")
async def google_disconnect(user: dict = Depends(get_current_user)):
    user_id = user['id']
    supabase_admin.table("users").update({
        "gmail_connected": False,
        "gmail_access_token": None,
        "gmail_refresh_token": None,
    }).eq("id", user_id).execute()
    return {"status": "success", "message": "Gmail disconnected"}
