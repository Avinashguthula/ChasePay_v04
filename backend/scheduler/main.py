from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.services.reminder_engine import process_overdue_invoices
import asyncio

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Run every 60 seconds for testing
    scheduler.add_job(process_overdue_invoices, 'interval', seconds=150)
    scheduler.start()
    print("Scheduler started: Checking for overdue invoices every 60 seconds.")
