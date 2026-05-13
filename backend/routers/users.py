from fastapi import APIRouter, Depends
from backend.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

from pydantic import BaseModel
from typing import Optional
from backend.db.supabase import supabase_admin

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bank_details: Optional[str] = None
    upi_id: Optional[str] = None
    reminders_paused: Optional[bool] = None

from backend.core.config import settings

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    # Fetch full profile from DB
    user_id = user["id"]
    profile_res = supabase_admin.table("users").select("*").eq("id", user_id).single().execute()
    profile_data = profile_res.data if profile_res.data else {}
    
    # Calculate invoice stats
    plan = profile_data.get("plan", "free")
    
    # Get current month's invoice count
    from datetime import datetime
    first_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    invoices_res = supabase_admin.table("invoices").select("id", count="exact").eq("user_id", user_id).gte("created_at", first_of_month).execute()
    count = invoices_res.count if invoices_res.count is not None else 0
    
    limit = settings.PLAN_LIMITS.get(plan, 3)
    remaining = max(0, limit - count) if limit != float('inf') else "Unlimited"
    display_limit = "Unlimited" if limit == float('inf') else limit
    
    # Merge all data
    full_user = {**user, **profile_data}
    full_user["invoice_count"] = count
    full_user["invoice_limit"] = display_limit
    full_user["invoice_remaining"] = remaining
    
    print(f"DEBUG: Returning full_user: {full_user}")
    return full_user

@router.put("/me")
async def update_me(data: UserUpdate, user: dict = Depends(get_current_user)):
    user_id = user["id"]
    update_data = data.dict(exclude_unset=True)
    
    if not update_data:
        return user

    res = supabase_admin.table("users").update(update_data).eq("id", user_id).execute()
    return res.data[0] if res.data else user

@router.delete("/me")
async def delete_me(user: dict = Depends(get_current_user)):
    user_id = user["id"]
    # 1. Delete from public.users (cascade should handle clients/invoices)
    supabase_admin.table("users").delete().eq("id", user_id).execute()
    
    # 2. Delete from auth.users via admin API
    supabase_admin.auth.admin.delete_user(user_id)
    
    return {"status": "success", "message": "Account deleted permanently."}
