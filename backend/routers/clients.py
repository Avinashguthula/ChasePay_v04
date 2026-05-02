from fastapi import APIRouter, Depends, HTTPException
from backend.core.security import get_current_user
from backend.db.supabase import get_supabase_client, supabase_admin
from backend.core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/clients", tags=["Clients"])

class ClientCreate(BaseModel):
    name: str
    email: str

@router.get("/")
async def get_clients(user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    response = supabase.table("clients").select("*").execute()
    return response.data

@router.post("/")
async def create_client(client_data: ClientCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    
    # Check plan limits
    user_res = supabase_admin.table("users").select("plan").eq("id", user["id"]).single().execute()
    user_plan = user_res.data.get("plan", "free") if user_res.data else "free"
    limit = settings.PLAN_LIMITS.get(user_plan, 3)
    
    count_res = supabase_admin.table("clients").select("id", count="exact").eq("user_id", user["id"]).execute()
    current_count = count_res.count if count_res.count is not None else 0
    
    if current_count >= limit:
        raise HTTPException(status_code=403, detail=f"Client limit reached for {user_plan} plan. Upgrade to add more.")
    
    data = {
        "user_id": user["id"],
        "name": client_data.name,
        "email": client_data.email
    }
    response = supabase.table("clients").insert(data).execute()
    return response.data[0]

@router.delete("/{client_id}")
async def delete_client(client_id: str, user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    response = supabase.table("clients").delete().eq("id", client_id).execute()
    return {"message": "Client deleted"}
