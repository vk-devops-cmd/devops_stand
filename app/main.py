import os
import time
import logging
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

POSTGRES_DSN = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST', 'db')}:{os.getenv('POSTGRES_PORT', 5432)}"
    f"/{os.getenv('POSTGRES_DB')}"
)
REDIS_URL = (
    f"redis://:{os.getenv('REDIS_PASSWORD', '')}@"
    f"{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}/0"
)

db_pool: asyncpg.Pool | None = None
redis_client: redis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    db_pool = None
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    for attempt in range(10):
        try:
            db_pool = await asyncpg.create_pool(POSTGRES_DSN, min_size=1, max_size=5)
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS visits (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMPTZ DEFAULT now()
                    )
                    """
                )
            logger.info("Postgres pool initialized")
            break
        except Exception as exc:  # noqa: BLE001
            logger.warning("Postgres not ready (attempt %s): %s", attempt + 1, exc)
            time.sleep(2)

    yield

    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()


app = FastAPI(title="Test Stand App", lifespan=lifespan)


@app.get("/health")
async def health():
    """Health-check эндпоинт для docker healthcheck и nginx."""
    return {"status": "ok"}


@app.get("/")
async def root(request: Request):
    # Redis используется как кэш сессий/счётчик визитов
    visits = 0
    if redis_client:
        try:
            visits = await redis_client.incr("visits")
        except Exception as exc:  # noqa: BLE001
            logger.error("Redis error: %s", exc)

    db_status = "unknown"
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.execute("INSERT INTO visits DEFAULT VALUES")
                total = await conn.fetchval("SELECT count(*) FROM visits")
            db_status = f"ok, rows={total}"
        except Exception as exc:  # noqa: BLE001
            logger.error("Postgres error: %s", exc)
            db_status = "error"

    return JSONResponse(
        {
            "message": "Hello from FastAPI backend",
            "redis_visits": visits,
            "postgres_status": db_status,
            "client_headers": {
                "x-forwarded-for": request.headers.get("x-forwarded-for"),
                "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
                "x-forwarded-host": request.headers.get("x-forwarded-host"),
                "host": request.headers.get("host"),
            },
        }
    )
