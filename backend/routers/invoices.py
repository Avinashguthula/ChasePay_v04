from fastapi import APIRouter, Depends, HTTPException
from backend.core.security import get_current_user
from backend.db.supabase import get_supabase_client, supabase_admin
from backend.core.config import settings
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

router = APIRouter(prefix="/invoices", tags=["Invoices"])

class InvoiceCreate(BaseModel):
    client_name: str
    client_email: str
    amount: float
    currency: str = "USD"
    due_date: date
    description: Optional[str] = None

class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    description: Optional[str] = None

@router.get("/stats/summary")
async def get_invoice_stats(user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    response = supabase.table("invoices").select("*").execute()
    invoices = response.data
    
    today = date.today()
    total = len(invoices)
    paid = len([i for i in invoices if i["status"] == "paid"])
    unpaid = len([i for i in invoices if i["status"] == "unpaid"])
    overdue = len([i for i in invoices if i["status"] == "unpaid" and datetime.strptime(i["due_date"], "%Y-%m-%d").date() < today])
    
    return {
        "total": total,
        "paid": paid,
        "unpaid": unpaid,
        "overdue": overdue
    }

@router.get("/")
async def get_invoices(user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    response = supabase.table("invoices").select("*").order("created_at", desc=True).execute()
    return response.data

@router.post("/")
async def create_invoice(invoice: InvoiceCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    
    # Check plan limits
    user_res = supabase_admin.table("users").select("plan").eq("id", user["id"]).single().execute()
    user_plan = user_res.data.get("plan", "free") if user_res.data else "free"
    limit = settings.PLAN_LIMITS.get(user_plan, 3)
    
    # Use supabase_admin for count to ensure accuracy regardless of RLS
    count_res = supabase_admin.table("invoices").select("id", count="exact").eq("user_id", user["id"]).execute()
    current_count = count_res.count if count_res.count is not None else 0
    
    print(f"DEBUG: User {user['email']} (Plan: {user_plan}) has {current_count}/{limit} invoices")
    
    if current_count >= limit:
        print(f"DEBUG: Limit reached! Blocking creation.")
        raise HTTPException(status_code=403, detail=f"Invoice limit reached for {user_plan} plan. Upgrade to add more.")

    # Ensure client exists in clients table (and check client limits)
    client_res = supabase_admin.table("clients").select("*").eq("user_id", user["id"]).eq("email", invoice.client_email).execute()
    if not client_res.data:
        # Check client limit before adding new client
        client_count_res = supabase_admin.table("clients").select("id", count="exact").eq("user_id", user["id"]).execute()
        client_count = client_count_res.count if client_count_res.count is not None else 0
        print(f"DEBUG: User has {client_count}/{limit} clients. Adding new client: {invoice.client_email}")
        if client_count >= limit:
            raise HTTPException(status_code=403, detail=f"Client limit reached for {user_plan} plan. Cannot add new client.")
        
        supabase_admin.table("clients").insert({
            "user_id": user["id"],
            "name": invoice.client_name,
            "email": invoice.client_email
        }).execute()
    else:
        print(f"DEBUG: Client {invoice.client_email} already exists.")
    
    data = {
        "user_id": user["id"],
        "client_name": invoice.client_name,
        "client_email": invoice.client_email,
        "amount": invoice.amount,
        "currency": invoice.currency,
        "due_date": str(invoice.due_date),
        "description": invoice.description,
        "status": "unpaid"
    }
    response = supabase.table("invoices").insert(data).execute()
    return response.data[0]

@router.patch("/{invoice_id}/paid")
async def mark_invoice_paid(invoice_id: str, user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    response = supabase.table("invoices").update({"status": "paid"}).eq("id", invoice_id).execute()
    return response.data[0]

@router.patch("/{invoice_id}")
async def update_invoice(invoice_id: str, update: InvoiceUpdate, user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    
    update_data = {}
    if update.status is not None: update_data["status"] = update.status
    if update.amount is not None: update_data["amount"] = update.amount
    if update.due_date is not None: update_data["due_date"] = str(update.due_date)
    if update.description is not None: update_data["description"] = update.description
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    response = supabase.table("invoices").update(update_data).eq("id", invoice_id).execute()
    return response.data[0]

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str, user: dict = Depends(get_current_user)):
    supabase = get_supabase_client(user["token"])
    supabase.table("invoices").delete().eq("id", invoice_id).execute()
    return {"message": "Invoice deleted"}
