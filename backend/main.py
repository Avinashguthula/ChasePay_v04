from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import invoices, clients, payments, google_oauth, auth
from backend.scheduler.main import start_scheduler
from backend.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(google_oauth.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
async def root():
    return {"message": "ChasePay API is running"}
