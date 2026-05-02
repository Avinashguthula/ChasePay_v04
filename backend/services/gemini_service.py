import google.generativeai as genai
from backend.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_reminder_email(client_name: str, amount: float, currency: str, days_overdue: int, reminder_type: str, description: str = None):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Generate a professional and polite payment reminder email.
    
    Context:
    - Client Name: {client_name}
    - Invoice Description: {description if description else "Professional Services"}
    - Amount Due: {amount} {currency}
    - Days Overdue: {days_overdue}
    - Reminder Type: {reminder_type} (options: day1, day3, day7)
    
    Tone:
    - day1: Friendly and gentle nudge.
    - day3: Firm but professional follow-up.
    - day7: Urgent final notice before further action.
    
    Output only the subject and the body of the email in a clear format.
    Ensure the email mentions the 'Invoice Description' so the client knows exactly what they are being billed for.
    """
    
    response = model.generate_content(prompt)
    return response.text
