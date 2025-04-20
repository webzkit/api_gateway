from logging import Logger
from typing import Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from core.helpers.utils import sanitize_path
from config import settings
from core.monitors.logger import Logger
import jwt
from datetime import datetime
from core.db.redis.redis_pool import redis_pool

logger = Logger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    SKIP_RATE_LIMIT_PATHS = ["health", "index", "api_v1_authenticate_login"]

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def get_uname(self, request: Request) -> str:
        try:
            token = (request.headers.get("Authorization") or "").replace("Bearer ", "")
            payload = jwt.decode(token, options={"verify_signature": False})

            return payload["payload"]["username"]

        except Exception:
            return request.client.host  # pyright: ignore

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response | Any:
        path = sanitize_path(request.url.path) or "index"

        if path in self.SKIP_RATE_LIMIT_PATHS:
            return await call_next(request)

        uname = await self.get_uname(request)  # pyright: ignore

        try:
            is_limited = await self.is_rate_limited(
                uname=uname,
                path=path,
                limit=settings.REDIS_RATE_LIMIT_TIME,
                period=settings.REDIS_RATE_LIMIT_PERIOD,
            )

            if is_limited:
                logger.warning(f"Rate limit exceeded for user {uname} on path {path}")
                return JSONResponse(
                    content={"detail": "Rate limit exceeded."}, status_code=429
                )
        except Exception as e:
            logger.error(f"{e}")

        return await call_next(request)

    async def is_rate_limited(
        self, uname: str, path: str, limit: int, period: int
    ) -> bool:
        if redis_pool.client() is None:
            logger.error("Redis client is not initialized.")
            raise Exception("Redis client is not initialized")

        current_timestamp = int(datetime.now().timestamp())
        window_start = current_timestamp - (current_timestamp % period)

        sanitized_path = sanitize_path(path)
        key = f"rate_limit:{uname}:{sanitized_path}:{window_start}"

        try:
            current_count = await redis_pool.client().incr(key)
            if current_count == 1:
                await redis_pool.client().expire(key, period)

            if current_count > limit:
                return True

        except Exception as e:
            raise e

        return False
