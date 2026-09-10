import resend
from backend.core.config import settings
from backend.db.supabase import supabase_admin
import httpx

resend.api_key = settings.RESEND_API_KEY

async def send_email_unified(user_id: str, to_email: str, subject: str, body: str, sender_name: str = None):
    # Fetch user details for plan and Gmail connection
    user_res = supabase_admin.table("users").select("*").eq("id", user_id).single().execute()
    user_data = user_res.data
    
    plan = user_data.get("plan", "free")
    gmail_connected = user_data.get("gmail_connected", False)

    # Initialise sent flag
    sent = False

    # Pro/Agency accounts should use Gmail (own domain) when tokens are present
    if plan in ["pro", "agency"] and gmail_connected:
        # Ensure Gmail tokens exist before attempting Gmail send
        if user_data.get('gmail_access_token') and user_data.get('gmail_refresh_token'):
            try:
                # Pass sender_name via user_data for Gmail From header
                user_data['sender_name'] = sender_name
                sent = await send_via_gmail(user_data, to_email, subject, body)
            except Exception as e:
                print(f"Gmail failed for {user_id}: {e}, falling back to Resend")
                sent = False
        else:
            print(f"[WARN] Missing Gmail tokens for user {user_id}, using Resend fallback")
            sent = False
            
    if not sent:
        # Send via Resend (Free tier or fallback)
        try:
            params = {
                "from": f"{sender_name} <{settings.FROM_EMAIL}>" if sender_name else settings.FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": body.replace("\n", "<br>"),
            }
            resend.Emails.send(params)
            return True
        except Exception as e:
            print(f"Resend failed: {e}")
            return False
    return True

async def send_via_gmail(user_data: dict, to: str, subject: str, body: str):
    # Requires valid Gmail tokens and Google API setup
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import base64
    from email.message import EmailMessage
    # Debug token presence (redacted)
    print(f"[DEBUG] Gmail tokens - access: {'YES' if user_data.get('gmail_access_token') else 'NO'}, refresh: {'YES' if user_data.get('gmail_refresh_token') else 'NO'}")
    try:
        creds = Credentials(
            token=user_data.get('gmail_access_token'),
            refresh_token=user_data.get('gmail_refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
    except Exception as e:
        print(f"[ERROR] Failed to create Gmail credentials: {e}")
        raise
    # Refresh token if needed
    try:
        from google.auth.transport.requests import Request
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    except Exception as e:
        print(f"[WARN] Token refresh issue: {e}")
    service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['Subject'] = subject
    # Set From header, optionally with sender name
    profile = service.users().getProfile(userId='me').execute()
    user_email = profile.get('emailAddress')
    if user_email:
        sender_name = user_data.get('sender_name')
        if sender_name:
            message['From'] = f"{sender_name} <{user_email}>"
        else:
            message['From'] = user_email
    else:
        print(f"[WARN] No Gmail profile email for user {user_data.get('id')}")
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    service.users().messages().send(userId='me', body=create_message).execute()
    return True
