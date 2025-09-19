from fastapi import FastAPI, Depends
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, get_db
from job_schdular.schdular import start_scheduler
from model.models import Base, JobLog
from tasks import sample_job
from sqlalchemy.future import select

app = FastAPI()
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Create tables if they don’t exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # start APScheduler
    start_scheduler()



# @app.get("/logs")
# async def get_logs(db: AsyncSession = Depends(get_db)):
#     result = await db.execute("SELECT * FROM job_logs ORDER BY created_at DESC LIMIT 10")
#     rows = result.fetchall()
#     return [dict(r) for r in rows]

@app.get("/logs")
async def get_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JobLog).order_by(JobLog.created_at.desc()).limit(10)
    )
    rows = result.scalars().all()
    return rows