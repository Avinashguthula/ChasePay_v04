from fastapi import APIRouter, HTTPException
from backend.db.supabase import get_supabase_client, call_with_retry
from backend.core.config import settings
from pydantic import BaseModel

from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthData(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.post("/signup")
async def signup(data: AuthData):
    supabase = get_supabase_client()
    try:
        signup_data = {
            "email": data.email,
            "password": data.password
        }
        
        if data.first_name or data.last_name:
            signup_data["options"] = {
                "data": {
                    "first_name": data.first_name,
                    "last_name": data.last_name
                }
            }
            
        response = call_with_retry(lambda: supabase.auth.sign_up(signup_data))
        return {"message": "User created", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(data: AuthData):
    supabase = get_supabase_client()
    try:
        response = call_with_retry(lambda: supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        }))
        return {
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
async def reset_password(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    supabase = get_supabase_client()
    try:
        print(f"DEBUG: Attempting password reset for {email}")
        call_with_retry(lambda: supabase.auth.reset_password_for_email(email, {
            "redirect_to": f"{settings.FRONTEND_URL}/update-password.html"
        }))
        print("DEBUG: Password reset email sent successfully")
        return {"message": "Password reset email sent"}
    except Exception as e:
        print(f"ERROR: Supabase Reset Password Failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-password")
async def update_password(data: dict):
    password = data.get("password")
    token = data.get("token")
    if not password or not token:
        raise HTTPException(status_code=400, detail="Password and token are required")
    
    supabase = get_supabase_client()
    try:
        # We need to set the session first to use the token
        call_with_retry(lambda: supabase.auth.set_session(token, ""))
        call_with_retry(lambda: supabase.auth.update_user({"password": password}))
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
