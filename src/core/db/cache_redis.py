from logging import Logger
from typing import Any
from redis.asyncio import ConnectionPool, Redis, RedisError
from config import settings
from abc import ABC, abstractmethod

logger = Logger(__name__)


class CacheInterface(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        pass

    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def has(self, key: str) -> bool:
        pass


class RedisCache(CacheInterface):
    def __init__(self):
        self.pool = ConnectionPool.from_url(settings.REDIS_CACHE_URL)
        self.client = Redis.from_pool(self.pool)

    async def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        try:
            await self.client.set(key, value)
            if ttl > 0:
                await self.client.expire(key, ttl)
            return True
        except RedisError as e:
            logger.error(f"Redis set error: {str(e)}")

            return False

    async def get(self, key: str) -> Any:
        try:
            return await self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis get error: {str(e)}")

            return None

    async def delete(self, key: str) -> bool:
        try:
            return bool(await self.client.delete(key))
        except RedisError as e:
            logger.error(f"Redis delete error: {str(e)}")

            return False

    async def has(self, key: str) -> bool:
        try:
            return await self.client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis has error: {str(e)}")

            return False

    async def close(self):
        try:
            await self.client.aclose()
            logger.info("Redis connection closed")
        except RedisError as e:
            logger.error(f"Redis closes error: {e}")


cache = RedisCache()
