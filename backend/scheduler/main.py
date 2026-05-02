from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.services.reminder_engine import process_overdue_invoices
import asyncio

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Run every 12 hours
    scheduler.add_job(process_overdue_invoices, 'interval', hours=12)
    scheduler.start()
    print("Scheduler started: Checking for overdue invoices every 12 hours.")
