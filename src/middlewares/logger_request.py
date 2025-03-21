from typing import Any
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.types import Message
import json
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from core.helpers.utils import parse_query_str
from core.logger import logging

logger = logging.getLogger("http-request")


class LoggerRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def get_current_user(self, request: Request) -> Response | Any:
        request_headeers = request.headers
        print(request_headeers)

        return 10

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        print(await self.get_current_user(request))
        logger.info(f"Request: {request.method} {request.url}")
        response: Response = await call_next(request)
        logger.info(f"Response: {response.status_code}")

        return response
