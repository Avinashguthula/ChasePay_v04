import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import invoices, clients, payments, google_oauth, auth, users
from backend.scheduler.main import start_scheduler
from backend.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(google_oauth.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "online"}

@app.get("/api/config")
async def get_public_config():
    """Return only public (non-secret) configuration values needed by the browser."""
    return {
        "api_url": settings.API_URL,
        "frontend_url": settings.FRONTEND_URL,
        "supabase_url": settings.SUPABASE_URL,
    }

# Serve static files from the frontend directory
# We use a custom route to handle extension-less URLs like /dashboard
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"))

@app.get("/invoices")
async def get_invoices():
    return FileResponse(os.path.join(frontend_dir, "invoices.html"))

@app.get("/create-invoice")
async def get_create_invoice():
    return FileResponse(os.path.join(frontend_dir, "create-invoice.html"))

@app.get("/settings")
async def get_settings():
    return FileResponse(os.path.join(frontend_dir, "settings.html"))

@app.get("/api/test/trigger-reminders")
async def trigger_reminders():
    from backend.services.reminder_engine import process_overdue_invoices
    await process_overdue_invoices()
    return {"status": "success", "message": "Reminders processed!"}

# Mount the rest of the static files (js, css, images)
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
