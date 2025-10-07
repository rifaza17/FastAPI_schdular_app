from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base
from app.service.database import engine
from app.service.ticker_service import fetch_and_store_stock, fetch_trending_symbols

scheduler = AsyncIOScheduler()

async def update_stocks():
    async with AsyncSession(engine) as db:
        symbols = await fetch_trending_symbols()
        print("📈 Trending symbols:", symbols)

        for symbol in symbols:
            await fetch_and_store_stock(symbol, db)

async def start_scheduler():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler.start()
    scheduler.add_job(update_stocks, "interval", minutes=10)