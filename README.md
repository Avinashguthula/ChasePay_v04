# ChasePay Backend

ChasePay is a production-ready SaaS backend for automated invoice tracking and reminders.

## Project Structure
```
backend/
├── main.py              # Entry point
├── core/
│   ├── config.py        # Configuration & Settings
│   ├── security.py      # JWT & Auth logic
├── db/
│   ├── supabase.py      # DB clients (User & Admin)
├── routers/
│   ├── invoices.py      # Invoice CRUD & Stats
│   ├── clients.py       # Client management & Plan limits
│   ├── payments.py      # Razorpay & Webhooks
│   ├── google_oauth.py  # Gmail Connection
├── services/
│   ├── email_service.py # Resend + Gmail Unified Sender
│   ├── gemini_service.py# AI Content Generation
│   ├── reminder_engine.py# Overdue Logic
├── scheduler/
│   ├── main.py          # APScheduler Configuration
├── .env                 # Secrets
└── requirements.txt     # Dependencies
```

## Setup Instructions

1. **Prerequisites**:
   - Python 3.9+
   - Supabase Account
   - Razorpay Account (Test Mode)
   - Resend API Key
   - Google Cloud Project (for Gmail API)

2. **Database Setup**:
   - Create a new Supabase project.
   - Run the provided SQL migrations in the Supabase SQL Editor (see `backend/db/initial_schema.sql` if provided, or use the one I applied).

3. **Backend Configuration**:
   - Navigate to the `backend` folder.
   - Copy `.env` and fill in the required keys.
   - **CRITICAL**: Update `SUPABASE_SERVICE_ROLE_KEY` from your Supabase Dashboard.

4. **Installation**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Run the Server**:
   ```bash
   uvicorn main:app --reload
   ```

6. **Frontend**:
   - Open `frontend/index.html` using a local server (e.g., Live Server in VS Code at http://localhost:5500).
   - Ensure the `api.js` points to `http://localhost:8000/api`.

## Core Logic
- **Reminders**: APScheduler runs every 12 hours, checks for unpaid invoices past due date, generates AI emails via Gemini, and sends via Gmail (if Pro) or Resend (Free/Fallback).
- **Limits**: Free users are capped at 3 clients. Pro at 20. Agency is unlimited.
- **Security**: Supabase RLS ensures data isolation. Backend validates JWT on every request.
