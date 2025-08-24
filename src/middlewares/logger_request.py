from typing import Any
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from core.monitors.logger import Logger
from core.helpers.utils import sanitize_path
import jwt

logger = Logger("http-request", filename="http-request.log")
SKIP_LOGGER = ["health", "metrics"]


class LoggerRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def get_uname(self, request: Request) -> Response | Any:
        try:
            token = (request.headers.get("Authorization") or "").replace("Bearer ", "")
            payload = jwt.decode(token, options={"verify_signature": False})

            return payload["payload"]["username"]

        except Exception:
            return request.client.host  # pyright: ignore

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

        uname = await self.get_uname(request)
        client_host = request.client.host  # pyright: ignore
        request_body = await self.get_body(request)

        # logger.warning(f"Test Warning")
        # logger.critical(f"Test Critical")
        # logger.info(f"Test Info")
        # logger.error(f"Test Error")
        # logger.debug(f"Test Debug")

        response: Response = await call_next(request)

        # Log acccess
        logger.info(
            f"Request: {request.method} {request.url}",
            extra={
                "uname": uname,
                "client_host": client_host,
                "request_body": request_body,
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )

        return response
