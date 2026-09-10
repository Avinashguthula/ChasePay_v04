from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.services.reminder_engine import process_overdue_invoices


def start_scheduler():
    scheduler = AsyncIOScheduler(
        timezone=ZoneInfo("Asia/Kolkata")
    )

    # Run every day at 9:00 AM IST
    scheduler.add_job(
        process_overdue_invoices,
        'cron',
        hour=9,
        minute=0
    )
    scheduler.start()
    print("Scheduler started: Checking for overdue invoices every day at 9 AM IST.")