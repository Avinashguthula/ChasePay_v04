import google.generativeai as genai
from backend.core.config import settings
import httpx

# Configure Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)


def generate_reminder_email(
    client_name: str,
    amount: float,
    currency: str,
    days_overdue: int,
    reminder_type: str,
    user_data: dict,
    description: str = None,
) -> str:
    """Generate a payment‑reminder email using AI.

    For **pro** and **agency** accounts the flow is:
    1. Try Gemini first.
    2. If Gemini fails, try Groq.
    3. If both fail, raise an exception – the caller will fall back to a static template.
    For **free** accounts we skip Gemini and go straight to Groq (or fallback).
    """
    user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or user_data.get(
        "email", "Your Billing Team"
    )
    plan = user_data.get("plan", "free")
    company_name = user_data.get("company_name", "")
    website = user_data.get("website", "")
    address = user_data.get("address", "")
    bank_details = user_data.get("bank_details", "")
    upi_id = user_data.get("upi_id", "")

    # Build optional payment block
    payment_block = ""
    if bank_details or upi_id:
        payment_block = "\nPayment Details:\n"
        if bank_details:
            payment_block += f"- Bank: {bank_details}\n"
        if upi_id:
            payment_block += f"- UPI ID: {upi_id}\n"

    # Branding instructions based on plan
    if plan == "agency":
        branding_instruction = f"""
BRANDING: This is a WHITE‑LABEL email.
- DO NOT mention 'Orlina' or 'ChasePay' anywhere.
- Use the following signature:
  Best regards,
  {user_name}
  {company_name}
  {user_data.get('phone', '')}
"""
    else:
        branding_instruction = f"""
BRANDING: Include mandatory branding.
- Add 'Sent via ChasePay' or 'Powered by ChasePay' at the very end of the email.
- Ensure the subject or body mentions: 'Invoice reminder from {user_name}'.
- Use the following signature format:
  Best regards,
  {user_name}
  {company_name}
  Powered by ChasePay
"""

    # Prompt that both models will receive
    prompt = f"""
Generate a professional and polite payment reminder email.

Context:
- Client Name: {client_name}
- Sender Name (User): {user_name}
- Company: {company_name}
- Website: {website}
- Address: {address}
- Invoice Description: {description if description else 'Professional Services'}
- Amount Due: {amount} {currency}
- Days Overdue: {days_overdue}
- Reminder Type: {reminder_type} (day1=friendly, day3=firm, day7=urgent)

{payment_block}
{branding_instruction}

Instructions:
- Format as: Subject: ... followed by Body: ...
- If payment details are provided above, include them clearly in the body.
- Mention the 'Invoice Description' clearly.
- Ensure the tone matches the reminder type.
"""

    def call_gemini() -> str:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text

    def call_groq() -> str:
        if not settings.GROQ_API_KEY:
            raise Exception("No Groq API key")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        # Debug: show request payload size
        print(f"[DEBUG] Sending request to Groq API with payload keys: {list(data.keys())}")
        with httpx.Client() as client:
            resp = client.post(url, headers=headers, json=data)
            print(f"[DEBUG] Groq API response status: {resp.status_code}")
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]
            print(f"[DEBUG] Groq API response content length: {len(result)}")
            return result

    # Decision flow based on plan
    if plan in ["pro", "agency"]:
        # Try Gemini first
        try:
            return call_gemini()
        except Exception as gemini_err:
            print(f"Gemini API failed: {gemini_err}. Trying Groq...")
            try:
                print("[DEBUG] Invoking Groq API for fallback (Pro/Agency)")
                return call_groq()
            except Exception as groq_err:
                print(f"Groq API failed: {groq_err}. Falling back to static template.")
                raise
    else:
        # Free tier – go straight to Groq
        try:
            print("[DEBUG] Invoking Groq API for Free tier")
            return call_groq()
        except Exception as groq_err:
            print(f"Groq API failed: {groq_err}. Falling back to static template.")
            raise
