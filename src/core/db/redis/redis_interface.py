from abc import ABC, abstractmethod
from typing import Any
from redis.asyncio import Redis


class RedisInterface(ABC):
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

    @abstractmethod
    def client(self) -> Redis:
        pass
