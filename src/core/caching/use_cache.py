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
            response_data, status_code = await func(request, *args, **kwargs)

            """
            response_data, status_code = await cache.set_expire(expiration).get(
                func, request, *args, **kwargs
            )
            """
            return response_data, status_code

        return inner

    return wrap
