from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.services.reminder_engine import process_overdue_invoices
import asyncio

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Run every 60 seconds for testing
    scheduler.add_job(process_overdue_invoices, 'cron', hour=9, minute=0)
    scheduler.start()
    print("Scheduler started: Checking for overdue invoices every day at 9 AM.")
