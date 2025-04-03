import functools
import json
import re
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from redis.asyncio import ConnectionPool, Redis

from config import EnviromentOption, settings

from ..exception.cache_exception import (
    CacheIdentificationInferenceError,
    InvalidRequestError,
    MissingClientError,
)

pool: ConnectionPool | None = None
client: Redis | None = None


def _infer_resource_id(
    kwargs: dict[str, Any], resource_id_type: type | tuple[type, ...]
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


def _extract_data_inside_brackets(input_string: str) -> list[str]:
    data_inside_brackets = re.findall(r"{(.*?)}", input_string)

    return data_inside_brackets


def _construct_data_dict(
    data_inside_brackets: list[str], kwargs: dict[str, Any]
) -> dict[str, Any]:
    data_dict = {}
    for key in data_inside_brackets:
        data_dict[key] = kwargs[key]

    return data_dict


def _format_prefix(prefix: str, kwargs: dict[str, Any]) -> str:
    data_inside_brackets = _extract_data_inside_brackets(prefix)
    data_dict = _construct_data_dict(data_inside_brackets, kwargs)
    formatted_prefix = prefix.format(**data_dict)

    return formatted_prefix


def _format_extra_data(
    to_invalidate_extra: dict[str, str], kwargs: dict[str, Any]
) -> dict[str, Any]:
    formatted_extra = {}
    for prefix, id_template in to_invalidate_extra.items():
        formatted_prefix = _format_prefix(prefix, kwargs)
        id = _extract_data_inside_brackets(id_template)[0]
        formatted_extra[formatted_prefix] = kwargs[id]

    return formatted_extra


async def _delete_keys_by_pattern(pattern: str) -> None:
    if client is None:
        raise MissingClientError

    cursor = -1
    while cursor != 0:
        cursor, keys = await client.scan(cursor, match=pattern, count=100)
        if keys:
            await client.delete(*keys)


def use_cache(expiration: int = 3600) -> Callable:
    def wrap(func) -> Callable:
        @functools.wraps(func)
        async def inner(request: Request, *args, **kwargs) -> Any:
            # Disabed at Development
            # if settings.APP_ENV == EnviromentOption.DEVELOPMENT.value:
            #    response_data, status_code = await func(request, *args, **kwargs)

            #    return response_data, status_code

            key_prefix = kwargs.get("cache_key_prefix", None)
            if key_prefix is None:
                response_data, status_code = await func(request, *args, **kwargs)

                return response_data, status_code
            else:
                if client is None:
                    raise MissingClientError

                if kwargs.get("cache_resource_id_name") is not None:
                    cache_kwargs = kwargs.get("cache_kwargs", {})
                    resource_id = cache_kwargs[kwargs.get("cache_resource_id_name")]
                else:
                    resource_id = _infer_resource_id(
                        kwargs=kwargs.get("cache_kwargs", {}),
                        resource_id_type=kwargs.get("cache_resource_id_type", int),
                    )

                formatted_key_prefix = _format_prefix(
                    key_prefix, kwargs.get("cache_kwargs", {})
                )
                cache_key = f"{formatted_key_prefix}:{resource_id}"

                if request.method == "GET":
                    cached_data = await client.get(cache_key)
                    if cached_data:
                        return json.loads(cached_data.decode()), None

                response_data, status_code = await func(request, *args, **kwargs)

                if request.method == "GET":
                    serializable_data = jsonable_encoder(response_data)
                    serialized_data = json.dumps(serializable_data)

                    await client.set(cache_key, serialized_data)
                    await client.expire(cache_key, expiration)

                    serialized_data = json.loads(serialized_data)

                else:
                    await client.delete(cache_key)

                return response_data, status_code

        return inner

    return wrap
