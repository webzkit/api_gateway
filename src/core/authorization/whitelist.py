import json
from typing import Dict, Optional

from fastapi.encoders import jsonable_encoder
from core.helpers import cache
from core.helpers.utils import hashkey
from core.exception.cache_exception import MissingClientError


class WhiteList:
    def __init__(self, username: Optional[str] = "unknown", payload: Dict = {}):
        self.__username = username
        self.__payload = payload
        self.__expire = 3600

    async def has_whitelist(self, key: str, token: str) -> bool:
        return await self.has(self.get_cache_key(key=key, token=token))

    async def revoke(self, key: str, token: str) -> None:
        await self.destroy(self.get_cache_key(key=key, token=token))

    async def has(self, key: str) -> bool:
        if cache.client is None:
            raise MissingClientError

        data = await cache.client.get(key)

        return False if not data else True

    async def destroy(self, key: str) -> None:
        if cache.client is None:
            raise MissingClientError

        await cache.client.delete(key)

    def get_cache_key(self, key: str, token: str):
        return f"whitelist_token:{self.__username}:{key}:{hashkey(token)}"

    async def store_access_token(self):
        await self.__store(
            key=self.get_cache_key(
                key="access_token", token=self.get_payload().get("access_token", "")
            ),
            data=self.get_payload(),
        )

    async def store_refresh_token(self):
        await self.__store(
            key=self.get_cache_key(
                key="refresh_token", token=self.get_payload().get("refresh_token", "")
            ),
            data=self.get_payload(),
        )

    async def __store(self, key: str, data: Dict) -> None:
        if cache.client is None:
            raise MissingClientError

        serializable_data = jsonable_encoder(data)
        serialized_data = json.dumps(serializable_data)

        await cache.client.set(key, serialized_data)
        await cache.client.expire(key, self.get_expire())

    def set_username(self, username: str):
        self.__username = username

        return self

    def get_username(self):
        return self.__username

    def set_payload(self, payload: Dict = {}):
        self.__payload = payload

        return self

    def get_payload(self):
        return self.__payload

    def set_expire(self, minute: int = 3600):
        self.__expire = minute

        return self

    def get_expire(self):
        return self.__expire * 60  # seconds
