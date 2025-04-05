from collections.abc import Callable
import functools
from typing import Any
from fastapi import Request
from .cache import Caching

cache = Caching()


def use_cache(expiration: int = 3600) -> Callable:
    def wrap(func) -> Callable:
        @functools.wraps(func)
        async def inner(request: Request, *args, **kwargs) -> Any:
            response_data, status_code = await cache.set_expire(expiration).aside(
                func, request, *args, **kwargs
            )

            return response_data, status_code

        return inner

    return wrap
