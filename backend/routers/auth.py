from fastapi import APIRouter, HTTPException
from backend.db.supabase import get_supabase_client
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthData(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(data: AuthData):
    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        return {"message": "User created", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(data: AuthData):
    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
