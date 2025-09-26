import ssl
from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from contextlib import asynccontextmanager

from app.core.config import settings


# Global Redis connection pool
_redis_pool: ConnectionPool = None
_redis_client: redis.Redis = None

async def connect_to_redis():
    """
    Initializes the Redis connection pool and client.
    Called on application startup.
    """
    global _redis_pool, _redis_client
    try:
        _redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,  # Decode responses to strings
            encoding="utf-8",
            max_connections=10,
            ssl_cert_reqs=ssl.CERT_NONE,
            ssl_check_hostname=False,
        )
        _redis_client = redis.Redis(connection_pool=_redis_pool)
        await _redis_client.ping()
        print("Redis connection successful!")
    except Exception as e:
        print(f"Could not connect to Redis: {e}")
        # In a real application, you might want to raise an exception or handle this more robustly

async def close_redis_connection():
    """
    Closes the Redis connection pool.
    Called on application shutdown.
    """
    global _redis_pool, _redis_client
    if _redis_client:
        await _redis_client.aclose()
        print("Redis connection closed.")
    if _redis_pool:
        await _redis_pool.disconnect()
        print("Redis pool disconnected.")

async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """
    FastAPI dependency to get a Redis client instance.
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Ensure connect_to_redis() is called on startup.")
    try:
        yield _redis_client
    finally:
        pass
    
# @asynccontextmanager
# def get_sync_redis():
#     """
#     For synchronous contexts (like Celery tasks)
#     Returns a sync Redis client using the same connection pool
#     """
#     import redis as sync_redis
#     if not _redis_pool:
#         raise RuntimeError("Redis not initialized")
#     return sync_redis.Redis(connection_pool=_redis_pool)

def get_sync_redis():
    import redis as sync_redis
    return sync_redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, ssl_cert_reqs=ssl.CERT_NONE, ssl_check_hostname=False)
