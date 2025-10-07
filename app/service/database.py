import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DB_HOST = "arenberg.cpi08wga2nbk.us-west-2.rds.amazonaws.com"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "arenberg123"
DB_NAME = "stockdb"

# Async URL (for app logic)
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Sync URL (to postgres default DB for management tasks)
DEFAULT_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"


def ensure_database():
    """Ensure stockdb exists, create if not."""
    engine = create_engine(DEFAULT_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:d"), {"d": DB_NAME}
        )
        exists = result.scalar()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"🎉 Database '{DB_NAME}' created successfully")
        else:
            print(f"✅ Database '{DB_NAME}' already exists")


# --- Async engine for app ---
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

