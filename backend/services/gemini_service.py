import google.generativeai as genai
from backend.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_reminder_email(client_name: str, amount: float, currency: str, days_overdue: int, reminder_type: str, user_data: dict, description: str = None):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip() or user_data.get("email", "Your Billing Team")
    plan = user_data.get("plan", "free")
    company_name = user_data.get('company_name', '')
    website = user_data.get('website', '')
    address = user_data.get('address', '')
    bank_details = user_data.get('bank_details', '')
    upi_id = user_data.get('upi_id', '')

    payment_block = ""
    if bank_details or upi_id:
        payment_block = "\nPayment Details:\n"
        if bank_details: payment_block += f"- Bank: {bank_details}\n"
        if upi_id: payment_block += f"- UPI ID: {upi_id}\n"

    branding_instruction = ""
    if plan == "agency":
        branding_instruction = f"""
        BRANDING: This is a WHITE-LABEL email. 
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
        - Add "Sent via ChasePay" or "Powered by ChasePay" at the very end of the email.
        - Ensure the subject or body mentions: "Invoice reminder from {user_name}"
        - Use the following signature format:
          Best regards,
          {user_name}
          {company_name}
          Powered by ChasePay
        """

    prompt = f"""
    Generate a professional and polite payment reminder email.
    
    Context:
    - Client Name: {client_name}
    - Sender Name (User): {user_name}
    - Company: {company_name}
    - Website: {website}
    - Address: {address}
    - Invoice Description: {description if description else "Professional Services"}
    - Amount Due: {amount} {currency}
    - Days Overdue: {days_overdue}
    - Reminder Type: {reminder_type} (day1=friendly, day3=firm, day7=urgent)

    {payment_block}

    {branding_instruction}
    
    Instructions:
    - Format as: Subject: ... followed by Body: ...
    - If payment details are provided above, include them clearly in the body to help the client pay.
    - Mention the 'Invoice Description' clearly.
    - Ensure the tone matches the reminder type.
    """
    
    response = model.generate_content(prompt)
    return response.text

