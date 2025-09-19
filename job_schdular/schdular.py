# app/job_scheduler/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine
from tasks import sample_job

scheduler = AsyncIOScheduler()

async def run_job():
    async with AsyncSession(engine) as db:
        await sample_job(db)

def start_scheduler():
    scheduler.start()
    # run every 10 minutes
    scheduler.add_job(run_job, "interval", minutes=10)
