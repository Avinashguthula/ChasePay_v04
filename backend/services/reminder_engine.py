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
                    # Prepare dynamic variables for fallback template
                    company_name = user_data.get("company_name") or ""
                    
                    # Brand name: White-label for agency, otherwise ChasePay
                    brand_name = "ChasePay"
                    if plan == "agency" and company_name:
                        brand_name = company_name
                        
                    support_email = user_data.get("email", "support@chasepay.com")
                    
                    due_date_str = inv.get("due_date", "")
                    due_date_html = ""
                    if due_date_str:
                        due_date_html = f"""
                                            <tr>
                                                <td style="padding-bottom: 12px; color: #666666; font-size: 14px;">Due Date</td>
                                                <td align="right" style="padding-bottom: 12px; font-weight: 600; color: #111111; font-size: 14px;">{due_date_str}</td>
                                            </tr>"""
                                            
                    invoice_url = inv.get("payment_url") or inv.get("invoice_url") or ""
                    cta_button_html = ""
                    if invoice_url:
                        cta_button_html = f"""
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 30px; margin-bottom: 30px;">
                                <tr>
                                    <td align="center">
                                        <a href="{invoice_url}" style="display: inline-block; padding: 14px 28px; background-color: #00c4cc; color: #ffffff; text-decoration: none; border-radius: 24px; font-size: 16px; font-weight: 600; text-align: center;">View invoice</a>
                                    </td>
                                </tr>
                            </table>
                        """
                        
                    footer_text = f"&copy; {datetime.now().year} {brand_name}. All rights reserved."

                    fallback_subject = f"Payment reminder | Invoice {inv['invoice_number']}"

                    fallback_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment reminder</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f0f1f5; font-family: 'Inter', Arial, Helvetica, sans-serif; color: #111111;">

    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f0f1f5; padding: 40px 15px;">
        <tr>
            <td align="center">

                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 40px; border-bottom: 1px solid #eeeeee;">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #111111;">
                                {brand_name}
                            </h1>
                        </td>
                    </tr>

                    <!-- Hero & Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 10px 0; font-size: 28px; font-weight: 700; color: #111111;">
                                Payment reminder
                            </h2>
                            <p style="margin: 0 0 30px 0; font-size: 16px; color: #555555;">
                                A quick reminder about your outstanding invoice from { user_name }.
                            </p>

                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6;">
                                Hi {inv['client_name']},<br><br>
                                This is a friendly reminder that your invoice is currently <strong>{days_overdue} days overdue</strong>. We would appreciate it if you could arrange payment at your earliest convenience.
                            </p>

                            <!-- Invoice Summary Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f9f9f9; border-radius: 8px; margin: 30px 0;">
                                <tr>
                                    <td style="padding: 24px;">
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td style="padding-bottom: 12px; color: #666666; font-size: 14px;">Invoice Number</td>
                                                <td align="right" style="padding-bottom: 12px; font-weight: 600; color: #111111; font-size: 14px;">{inv['invoice_number']}</td>
                                            </tr>{due_date_html}
                                            <tr>
                                                <td style="padding-top: 12px; border-top: 1px solid #eeeeee; color: #111111; font-size: 16px; font-weight: 600;">Outstanding Amount</td>
                                                <td align="right" style="padding-top: 12px; border-top: 1px solid #eeeeee; color: #00c4cc; font-size: 18px; font-weight: 700;">{inv['currency']} {inv['amount']}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 0 0 30px 0; font-size: 16px; line-height: 1.6;">
                                If payment has already been completed, please disregard this message.
                            </p>

                            {cta_button_html}

                        </td>
                    </tr>

                    <!-- Help Section -->
                    <tr>
                        <td style="padding: 40px; background-color: #111111; color: #ffffff;">
                            <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 600;">Need help?</h3>
                            <p style="margin: 0; font-size: 14px; color: #cccccc; line-height: 1.6;">
                                If you have any questions about this invoice, please contact us at <a href="mailto:{support_email}" style="color: #00c4cc; text-decoration: none;">{support_email}</a>.
                            </p>
                        </td>
                    </tr>
                    
                </table>

                <!-- Footer -->
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin-top: 20px;">
                    <tr>
                        <td align="center" style="font-size: 12px; color: #888888; line-height: 1.5;">
                            {footer_text}
                        </td>
                    </tr>
                </table>

            </td>
        </tr>
    </table>

</body>
</html>"""

                    # Attempt to generate AI email
                    email_content = None
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
                    except Exception as ai_err:
                        print(f"DEBUG: AI email generation failed: {ai_err}")

                    subject = fallback_subject
                    body = fallback_body

                    # Validate AI output
                    if email_content:
                        # Extract subject and body if possible
                        lines = email_content.split("\n")
                        ai_subject = lines[0].replace("Subject: ", "").strip()
                        ai_body = "\n".join(lines[1:]).strip()
                        
                        is_valid_html = False
                        if "<html" in ai_body.lower() and "<body" in ai_body.lower() and not ai_body.startswith("```"):
                            is_valid_html = True
                            
                        if is_valid_html:
                            subject = ai_subject or subject
                            body = ai_body
                            print("DEBUG: Using AI generated HTML email.")
                        else:
                            print("DEBUG: AI output is not valid HTML, using fallback template.")
                    
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
