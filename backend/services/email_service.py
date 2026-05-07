import resend
from backend.core.config import settings
from backend.db.supabase import supabase_admin
import httpx

resend.api_key = settings.RESEND_API_KEY

async def send_email_unified(user_id: str, to_email: str, subject: str, body: str):
    # Fetch user details for plan and Gmail connection
    user_res = supabase_admin.table("users").select("*").eq("id", user_id).single().execute()
    user_data = user_res.data
    
    plan = user_data.get("plan", "free")
    gmail_connected = user_data.get("gmail_connected", False)
    print(f"DEBUG: Unified Email Check - User: {user_id}, Plan: {plan}, Gmail Connected: {gmail_connected}")
    
    sent = False
    
    if plan in ["pro", "agency"] and gmail_connected:
        try:
            sent = await send_via_gmail(user_data, to_email, subject, body)
        except Exception as e:
            import traceback
            print(f"Gmail failed for {user_id}: {e}")
            traceback.print_exc()
            sent = False
            
    if not sent:
        # Send via Resend (Free tier or fallback)
        try:
            params = {
                "from": settings.FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": body.replace("\n", "<br>"),
            }
            print(f"DEBUG: Calling Resend API with params: {params}")
            resend.Emails.send(params)
            return True
        except Exception as e:
            print(f"RESEND ERROR: {e}")
            return False
    return True

async def send_via_gmail(user_data: dict, to: str, subject: str, body: str):
    # This requires valid Gmail tokens and Google API setup
    # Implementation using google-api-python-client
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import base64
    from email.message import EmailMessage

    creds = Credentials(
        token=user_data.get("gmail_access_token"),
        refresh_token=user_data.get("gmail_refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET
    )
    
    service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['Subject'] = subject
    
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    service.users().messages().send(userId="me", body=create_message).execute()
    return True
