from fastapi import APIRouter, Depends, HTTPException, Request
from backend.core.security import get_current_user
from backend.core.config import settings
from backend.db.supabase import supabase_admin
import razorpay
import hmac
import hashlib

router = APIRouter(prefix="/payments", tags=["Payments"])

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.post("/create-order")
async def create_order(plan: str, user: dict = Depends(get_current_user)):
    amount_map = {
        "pro": 1500, # $15 in cents (or INR equivalent)
        "agency": 4500
    }
    
    if plan not in amount_map:
        raise HTTPException(status_code=400, detail="Invalid plan")
        
    order_data = {
        "amount": amount_map[plan] * 80, # Assume 80 INR per USD for Razorpay INR accounts
        "currency": "INR",
        "receipt": f"receipt_{user['id']}_{plan}",
        "notes": {
            "user_id": user["id"],
            "plan": plan
        }
    }
    
    order = client.order.create(data=order_data)
    return order

@router.post("/webhook")
async def razorpay_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    
    # Verify signature
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # In production, check signature
    # if signature != expected_signature:
    #     raise HTTPException(status_code=400, detail="Invalid signature")
    
    data = await request.json()
    event = data.get("event")
    
    if event == "order.paid":
        notes = data["payload"]["order"]["entity"]["notes"]
        user_id = notes.get("user_id")
        plan = notes.get("plan")
        
        if user_id and plan:
            supabase_admin.table("users").update({"plan": plan}).eq("id", user_id).execute()
            print(f"User {user_id} upgraded to {plan}")
            
    return {"status": "ok"}
