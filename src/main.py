from fastapi import Request
from starlette.middleware.cors import CORSMiddleware
from typing import Any, Dict

from config import settings
from apis.v1.api import api_router
from core.setup import create_application
from core.logger import logging

logger = logging.getLogger("http")

# Init application
app = create_application(router=api_router, settings=settings)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # allow_origins=[str(origin)
        #               for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Middleware store request
"""
@app.middleware("http")
async def log_request(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")

    return response
"""


@app.get("/")
async def root() -> Any:
    result: Dict[Any, Any] = {
        "message": f"Your {settings.APP_NAME} endpoint is working"
    }

    return result


@app.get("/health")
def health_status():
    return {"status": "healthy"}
