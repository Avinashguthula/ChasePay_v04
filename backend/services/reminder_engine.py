from datetime import datetime, date, timedelta
from backend.db.supabase import supabase_admin
from backend.services.email_service import send_email_unified
from backend.services.gemini_service import generate_reminder_email

async def process_overdue_invoices():
    # Fetch unpaid invoices
    today = date.today()
    print(f"DEBUG: Starting process_overdue_invoices at {today}")
    
    invoices_res = supabase_admin.table("invoices").select("*").eq("status", "unpaid").execute()
    invoices = invoices_res.data
    print(f"DEBUG: Found {len(invoices)} unpaid invoices.")
    
    for inv in invoices:
        # Check if user has paused reminders
        user_res = supabase_admin.table("users").select("*").eq("id", inv["user_id"]).single().execute()
        user_data = user_res.data
        if user_data.get("reminders_paused"):
            print(f"DEBUG: Reminders paused for user {inv['user_id']}. Skipping invoice {inv['id']}")
            continue

        due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
        days_overdue = (today - due_date).days
        print(f"DEBUG: Invoice {inv['id']} for {inv['client_name']} is {days_overdue} days overdue.")
        
        reminder_type = None
        if days_overdue >= 7:
            reminder_type = "day7"
        elif days_overdue >= 3:
            reminder_type = "day3"
        elif days_overdue >= 1:
            reminder_type = "day1"
            
        if reminder_type:
            # Check if reminder already sent
            existing = supabase_admin.table("reminders").select("*").eq("invoice_id", inv["id"]).eq("type", reminder_type).execute()
            if not existing.data:
                try:
                    # Fetch user info for branding (already fetched above)
                    user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or user_data.get("email", "Your Billing Team")
                    plan = user_data.get("plan", "free")

                    # Generate AI email with branding
                    try:
                        email_content = generate_reminder_email(
                            inv["client_name"], 
                            inv["amount"], 
                            inv["currency"], 
                            days_overdue, 
                            reminder_type,
                            user_data,
                            inv.get("description")
                        )

                        # Split subject and body
                        lines = email_content.split("\n")
                        subject = lines[0].replace("Subject: ", "")
                        body = "\n".join(lines[1:])
                    except Exception as ai_err:
                        print(f"AI ERROR (Gemini): {ai_err}. Using fallback template.")
                        subject = f"Payment Reminder: Invoice {inv['invoice_number']}"
                        body = f"Hi {inv['client_name']},\n\nThis is a friendly reminder regarding invoice {inv['invoice_number']} for {inv['currency']} {inv['amount']} which is {days_overdue} days overdue. Please arrange for payment at your earliest convenience.\n\nBest regards,\nYour Billing Team"
                    
                    # Send email
                    print(f"DEBUG: Sending email via unified service...")
                    sender_name = user_name if plan == "agency" else "ChasePay"
                    success = await send_email_unified(inv["user_id"], inv["client_email"], subject, body, sender_name=sender_name)
                    
                    if success:
                        # Log reminder in reminders table
                        supabase_admin.table("reminders").insert({
                            "invoice_id": inv["id"],
                            "type": reminder_type
                        }).execute()
                        
                        # Update last_reminder in invoices table
                        supabase_admin.table("invoices").update({
                            "last_reminder": reminder_type
                        }).eq("id", inv["id"]).execute()
                        
                        print(f"SUCCESS: Sent {reminder_type} reminder for invoice {inv['id']}")
                    else:
                        print(f"ERROR: Email service returned False for invoice {inv['id']}")
                except Exception as e:
                    print(f"EXCEPTION: Failed to process reminder for {inv['id']}: {e}")
            else:
                print(f"DEBUG: {reminder_type} reminder already sent for {inv['id']}. Skipping.")
        else:
            print(f"DEBUG: Days overdue ({days_overdue}) does not match a reminder interval (1, 3, 7). Skipping.")
