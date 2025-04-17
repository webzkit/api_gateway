from collections.abc import Callable
import json
from typing import Self, Any
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from core.exception.cache_exception import (
    CacheIdentificationInferenceError,
    MissingClientError,
)
import re
from core.monitors.logger import Logger

# TODO refactor
from redis.asyncio import ConnectionPool, Redis
from config import settings

pool = ConnectionPool.from_url(settings.REDIS_CACHE_URL)
client = Redis.from_pool(pool)


logger = Logger(__name__)


class Caching:
    def __init__(self, expire: int = 3600) -> None:
        self.expire = expire
        self.key_prefix = ""

    def get_client(self):
        if client is None:
            raise MissingClientError

        return client

    async def aside(self, func: Callable, request: Request, *args, **kwargs) -> Any:
        self.key_prefix = kwargs.get("cache_key_prefix", None)

        if self.key_prefix is None:
            return await func(request, *args, **kwargs)

        cache_key = self.get_cache_key(**kwargs)

        if request.method == "GET":
            cache_data = await self.get_client().get(cache_key)
            if cache_data:
                return json.loads(cache_data.decode("utf-8")), None

        response_data, status_code = await func(request, *args, **kwargs)

        # Write to cache
        await self.__destroy_or_create(request, cache_key, response_data)

        return response_data, status_code

    async def __destroy_or_create(
        self, request: Request, key: str, response_data: dict = {}
    ) -> None:
        if request.method == "GET":
            await self.get_client().set(
                key, json.dumps(jsonable_encoder(response_data))
            )
            await self.get_client().expire(key, self.get_expire())

        else:
            await self.get_client().delete(key)

    def get_cache_key(self, **kwargs) -> str:
        formatted_key_prefix = self.__format_prefix(
            self.get_key_prefix(), kwargs.get("cache_kwargs", {})
        )

        return f"{formatted_key_prefix}:{self.__get_resource_id(**kwargs)}"

    def __get_resource_id(self, **kwargs) -> int | str:
        if kwargs.get("cache_resource_id_name") is not None:
            cache_kwargs = kwargs.get("cache_kwargs", {})
            return cache_kwargs[kwargs.get("cache_resource_id_name")]

        return self.__infer_resource_id(
            kwargs=kwargs.get("cache_kwargs", {}),
            resource_id_type=kwargs.get("cache_resource_id_type", int),
        )

    def set_expire(self, expire: int) -> Self:
        self.expire = expire

        return self

    def get_expire(self) -> int:
        return self.expire

    def set_key_prefix(self, key_prefix: str) -> Self:
        self.key_prefix = key_prefix

        return self

    def get_key_prefix(self) -> str:
        return self.key_prefix or ""

    def __infer_resource_id(
        self, kwargs: dict[str, Any], resource_id_type: type | tuple[type, ...]
    ) -> int | str:
        resource_id: int | str | None = None

        for arg_name, arg_value in kwargs.items():
            if isinstance(arg_value, resource_id_type):
                if (resource_id_type is int) and ("id" in arg_name):
                    resource_id = arg_value

                elif (resource_id_type is int) and ("id" not in arg_name):
                    pass

                elif resource_id_type is str:
                    resource_id = arg_value

        if resource_id is None:
            raise CacheIdentificationInferenceError

        return resource_id

    def __extract_data_inside_brackets(self, input_string: str) -> list[str]:
        data_inside_brackets = re.findall(r"{(.*?)}", input_string)

        return data_inside_brackets

    def __construct_data_dict(
        self, data_inside_brackets: list[str], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        data_dict = {}
        for key in data_inside_brackets:
            data_dict[key] = kwargs[key]

        return data_dict

    def __format_prefix(self, prefix: str, kwargs: dict[str, Any]) -> str:
        data_inside_brackets = self.__extract_data_inside_brackets(prefix)
        data_dict = self.__construct_data_dict(data_inside_brackets, kwargs)
        formatted_prefix = prefix.format(**data_dict)

        return formatted_prefix
