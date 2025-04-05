import json
from typing import Dict, Optional

from fastapi.encoders import jsonable_encoder
from core.db import cache_redis as cache

from core.helpers.utils import hashkey
from core.exception.cache_exception import MissingClientError
from core.monitors.logger import Logger


logger = Logger(__name__)


class WhiteList:
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    WHITELIST_TOKEN = "whitelist_token"

    def __init__(
        self,
        username: Optional[str] = "unknown",
        payload: Dict = {},
    ):
        self.__username = username
        self.__payload = payload
        self.__expire = 3600

    async def has_whitelist(self, key: str, token: str) -> bool:
        return await self.has(self.get_cache_key(key=key, token=token))

    async def revoke_all(self, key: str, token: Optional[str] = None) -> None:
        if token is None:
            return None
        try:
            data = await self.get(self.get_cache_key(key=key, token=token))
            if data is None:
                return None

            data = json.loads(jsonable_encoder(data))
            for key, value in data.items():
                if key == "bearer":
                    continue
                await self.destroy(self.get_cache_key(key=key, token=value))
        except Exception as e:
            logger.debug(f"{e}")
            return None

    async def get(self, key: str) -> Dict:
        if cache.client is None:
            raise MissingClientError

        return await cache.client.get(key)

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
        return f"{self.WHITELIST_TOKEN}:{self.__username}:{key}:{hashkey(token)}"

    async def store_access_token(self):
        await self.__store(
            key=self.get_cache_key(
                key=self.ACCESS_TOKEN,
                token=self.get_payload().get(self.ACCESS_TOKEN, ""),
            ),
            data=self.get_payload(),
        )

    async def store_refresh_token(self):
        await self.__store(
            key=self.get_cache_key(
                key=self.REFRESH_TOKEN,
                token=self.get_payload().get(self.REFRESH_TOKEN, ""),
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
