from sqlalchemy.ext.asyncio import AsyncSession
from model.models import JobLog

async def sample_job(db: AsyncSession):
    log = JobLog(message="Scheduled job ran successfully 🚀")
    db.add(log)
    await db.commit()
