from datetime import UTC, datetime
from typing import Union
from redis.asyncio import ConnectionPool, Redis

from core.logger import Logger
from schemas.rate_limit import sanitize_path

logger = Logger(__name__)

pool: ConnectionPool | None = None
client: Redis | None = None


async def is_rate_limited(
    user_id: Union[int, str], path: str, limit: int, period: int
) -> bool:
    if client is None:
        logger.error("Redis client is not initialized.")
        raise Exception("Redis client is not initialized.")

    current_timestamp = int(datetime.now().timestamp())
    window_start = current_timestamp - (current_timestamp % period)

    sanitized_path = sanitize_path(path)
    key = f"ratelimit:{user_id}:{sanitized_path}:{window_start}"

    try:
        current_count = await client.incr(key)
        if current_count == 1:
            await client.expire(key, period)

        if current_count > limit:
            return True

    except Exception as e:
        logger.exception(
            f"Error checking rate limit for user {user_id} on path {path}: {e}"
        )
        raise e

    return False
