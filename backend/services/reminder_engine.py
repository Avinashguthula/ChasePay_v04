from datetime import datetime, date, timedelta
from backend.db.supabase import supabase_admin
from backend.services.email_service import send_email_unified
from backend.services.gemini_service import generate_reminder_email

async def process_overdue_invoices():
    # Fetch unpaid invoices
    today = date.today()
    invoices_res = supabase_admin.table("invoices").select("*").eq("status", "unpaid").execute()
    invoices = invoices_res.data
    
    for inv in invoices:
        due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
        days_overdue = (today - due_date).days
        
        reminder_type = None
        if days_overdue == 1:
            reminder_type = "day1"
        elif days_overdue == 3:
            reminder_type = "day3"
        elif days_overdue == 7:
            reminder_type = "day7"
            
        if reminder_type:
            # Check if reminder already sent
            existing = supabase_admin.table("reminders").select("*").eq("invoice_id", inv["id"]).eq("type", reminder_type).execute()
            if not existing.data:
                # Generate AI email
                email_content = generate_reminder_email(
                    inv["client_name"], 
                    inv["amount"], 
                    inv["currency"], 
                    days_overdue, 
                    reminder_type
                )
                
                # Split subject and body (Gemini output format varies, we'll do a simple split or use regex)
                lines = email_content.split("\n")
                subject = lines[0].replace("Subject: ", "")
                body = "\n".join(lines[1:])
                
                # Send email
                success = await send_email_unified(inv["user_id"], inv["client_email"], subject, body)
                
                if success:
                    # Log reminder
                    supabase_admin.table("reminders").insert({
                        "invoice_id": inv["id"],
                        "type": reminder_type
                    }).execute()
                    print(f"Sent {reminder_type} reminder for invoice {inv['id']}")
