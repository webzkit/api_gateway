from abc import ABC, abstractmethod
import hashlib
import json
from typing import Dict, Self
from fastapi.encoders import jsonable_encoder
from core.db.cache_redis import CacheInterface


class TokenStore(ABC):
    def __init__(self, cache: CacheInterface):
        self._cache = cache
        self.__ttl = 60

    @abstractmethod
    def gen_key_by(self, key: str, key_hash: str) -> str:
        pass

    async def create(self, key: str, value: dict = {}):
        await self._cache.set(
            key=key, value=self.serializable(value), ttl=self.get_ttl()
        )

    def gen_key(self, **kwargs) -> str:
        return f"{kwargs.get('key')}:{kwargs.get('uname')}"

    def replace_token_bearer(self, token: str):
        return token.replace("Bearer ", "")

    def serializable(self, data: Dict = {}):
        return json.dumps(jsonable_encoder(data))

    def hash(self, key: str) -> str:
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def set_ttl(self, ttl: int) -> Self:
        self.__ttl = ttl

        return self

    def get_ttl(self) -> int:
        return self.__ttl
