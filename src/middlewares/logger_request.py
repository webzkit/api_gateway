from typing import Any
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from core.monitors.logger import Logger
from core.security import get_current_user_by
from schemas.rate_limit import sanitize_path

logger = Logger("http-request", filename="http-request.log")
SKIP_LOGGER = ["health", "metrics"]


class LoggerRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def get_current_user(self, request: Request) -> Response | Any:
        user_at = await get_current_user_by(request.headers.get("Authorization"))
        if user_at is None:
            return request.client.host  # pyright: ignore

        return user_at["username"]

    async def get_body(self, request: Request) -> str:
        body = await request.body()

        return body.decode("utf-8", errors="replace")

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = sanitize_path(request.url.path)
        if path in SKIP_LOGGER:
            return await call_next(request)

        username = await self.get_current_user(request)
        client_host = request.client.host  # pyright: ignore
        request_body = await self.get_body(request)

        # logger.warning(f"Test Warning")
        # logger.critical(f"Test Critical")
        # logger.info(f"Test Info")
        # logger.error(f"Test Error")
        # logger.debug(f"Test Debug")

        response: Response = await call_next(request)

        logger.info(
            f"Request: {request.method} {request.url}",
            extra={
                "uname": username,
                "client_host": client_host,
                "request_body": request_body,
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )

        return response
