from logging import Logger
from typing import Any
from redis.asyncio import ConnectionPool, Redis, RedisError
from config import settings
from .redis_interface import RedisInterface


logger = Logger(__name__)


class RedisPool(RedisInterface):
    def __init__(self):
        self._pool = ConnectionPool.from_url(settings.REDIS_CACHE_URL)
        self._client = Redis.from_pool(self._pool)

    def client(self) -> Redis:
        return self._client

    async def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        try:
            await self._client.set(key, value)
            if ttl > 0:
                await self._client.expire(key, ttl)
            return True
        except RedisError as e:
            logger.error(f"Redis set error: {str(e)}")

            return False

    async def get(self, key: str) -> Any:
        try:
            return await self._client.get(key)
        except RedisError as e:
            logger.error(f"Redis get error: {str(e)}")

            return None

    async def delete(self, key: str) -> bool:
        try:
            return bool(await self._client.delete(key))
        except RedisError as e:
            logger.error(f"Redis delete error: {str(e)}")

            return False

    async def has(self, key: str) -> bool:
        try:
            return await self._client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis has error: {str(e)}")

            return False

    async def close(self):
        try:
            await self._client.aclose()
            logger.info("Redis connection closed")
        except RedisError as e:
            logger.error(f"Redis closes error: {e}")


redis_pool = RedisPool()
