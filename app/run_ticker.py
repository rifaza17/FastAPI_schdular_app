import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# run_ticker.py
import asyncio, logging, signal
from app.job_schdular.schedular import start_scheduler
from app.service.database import engine
from sqlalchemy import text

logger = logging.getLogger("ticker")
logging.basicConfig(level=logging.INFO)

shutting_down = False
_lock_conn = None

async def acquire_leader_lock():
    global _lock_conn
    try:
        _lock_conn = await engine.connect()
        res = await _lock_conn.execute(text("SELECT pg_try_advisory_lock(123456789)"))
        locked = res.scalar_one()
        if not locked:
            await _lock_conn.close()
            _lock_conn = None
            return False
        return True
    except Exception:
        if _lock_conn is not None:
            await _lock_conn.close()
        return False

async def release_leader_lock():
    global _lock_conn
    if _lock_conn is not None:
        try:
            await _lock_conn.execute(text("SELECT pg_advisory_unlock(123456789)"))
            await _lock_conn.close()
        except Exception:
            pass

def _on_signal():
    global shutting_down
    shutting_down = True
    logger.info("SIGTERM received")

async def shutdown():
    await release_leader_lock()
    await engine.dispose()
    logger.info("Shutdown complete")

async def main():
    leader = await acquire_leader_lock()
    if not leader:
        logger.info("Another leader exists. Exiting.")
        return

    await start_scheduler()
    logger.info("Scheduler started")
    while not shutting_down:
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        for s in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(s, _on_signal)
    except NotImplementedError:
        # Windows fallback
        logger.warning("Signal handlers not supported on this platform")

    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(shutdown())
        loop.close()