from abc import ABC, abstractmethod
import hashlib
import json
from typing import Dict, Self
from fastapi.encoders import jsonable_encoder
from core.db.cache_redis import CacheInterface


class TokenManage(ABC):
    def __init__(self, cache: CacheInterface):
        self._cache = cache
        self._ttl = 60

    @abstractmethod
    def get_key_by(self, key: str, key_hash: str) -> str:
        pass

    async def has(self, key: str, key_hash: str) -> bool:
        return await self._cache.has(key=self.get_key_by(key=key, key_hash=key_hash))

    async def create(self, key: str, value: dict = {}):
        await self._cache.set(
            key=key, value=self.serializable(value), ttl=self.get_ttl()
        )

    async def destroy(self, key: str, key_hash: str):
        result = await self._cache.get(
            key=self.get_key_by(key=key, key_hash=self._replace_token_bearer(key_hash))
        )

        if result:
            token = json.loads(jsonable_encoder(result))
            for k, v in token.items():
                if v == "bearer":
                    continue

                await self._cache.delete(
                    key=self.get_key_by(
                        key=self.gen_key(key=k, uname=self._get_uname_at(key)),
                        key_hash=v,
                    )
                )

    def gen_key(self, **kwargs) -> str:
        return f"{kwargs.get('key')}:{kwargs.get('uname')}"

    def _replace_token_bearer(self, token: str):
        return token.replace("Bearer ", "")

    def serializable(self, data: Dict = {}):
        return json.dumps(jsonable_encoder(data))

    def hash(self, key: str) -> str:
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def _get_uname_at(self, key: str):
        return key.split(":")[-1]

    def set_ttl(self, ttl: int) -> Self:
        self._ttl = ttl

        return self

    def get_ttl(self) -> int:
        return self._ttl
