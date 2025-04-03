from collections.abc import Callable
import functools
from typing import Any
from fastapi import Request
from core.helpers import cache
from .cache import Caching

cache = Caching()


def use_cache(expiration: int = 3600) -> Callable:
    def wrap(func) -> Callable:
        @functools.wraps(func)
        async def inner(request: Request, *args, **kwargs) -> Any:
            key_prefix = kwargs.get("cache_key_prefix", None)
            if key_prefix is None:
                response_data, status_code = await func(request, *args, **kwargs)

                return response_data, status_code

            # get To Cache

        return inner

    return wrap
