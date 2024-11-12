from typing import Any, AsyncGenerator, Callable
from fastapi import APIRouter, Depends, FastAPI
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from redis import asyncio as redis
from arq import create_pool
from arq.connections import RedisSettings
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
import fastapi
from fastapi.openapi.utils import get_openapi

from core.helpers import rate_limit

from config import (
    EnviromentOption,
    settings,
    AppSetting,
    CryptSetting,
    RedisRateLimiterSetting,
    ServiceSetting,
)
from apis.v1 import deps


# Rate limit
async def create_redis_rate_limit_pool() -> None:
    rate_limit.pool = redis.ConnectionPool.from_url(settings.REDIS_RATE_LIMIT_URL)
    rate_limit.client = redis.Redis.from_pool(rate_limit.pool)  # type: ignore


async def close_redis_rate_limit_pool() -> None:
    await rate_limit.client.aclose()  # type: ignore


def lifespan_factory(
    settings: AppSetting | CryptSetting | RedisRateLimiterSetting | ServiceSetting,
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        if isinstance(settings, RedisRateLimiterSetting):
            await create_redis_rate_limit_pool()

        yield

        if isinstance(settings, RedisRateLimiterSetting):
            await close_redis_rate_limit_pool()

    return lifespan


# Create Application
def create_application(
    router: APIRouter,
    settings: AppSetting | CryptSetting | RedisRateLimiterSetting | ServiceSetting,
    **kwargs: Any
) -> FastAPI:
    if isinstance(settings, AppSetting):
        to_update = {
            "title": settings.APP_NAME,
            "description": "Description",
            "docs_url": None,
            "redoc_url": None,
            "openapi_url": None,
        }

        kwargs.update(to_update)

    lifespan = lifespan_factory(settings)
    application = FastAPI(lifespan=lifespan, **kwargs)

    if isinstance(settings, AppSetting):
        application.include_router(
            router,
            prefix=settings.APP_API_PREFIX,
            dependencies=[Depends(deps.is_supper_admin)],
        )

    if isinstance(settings, AppSetting):
        if settings.APP_ENV != EnviromentOption.PRODUCTION.value:
            docs_router = APIRouter()

            if settings.APP_ENV != EnviromentOption.DEVELOPMENT.value:
                docs_router = APIRouter(dependencies=[Depends(deps.is_supper_admin)])

            @docs_router.get("/docs", include_in_schema=False)
            async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
                return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/redoc", include_in_schema=False)
            async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
                return get_redoc_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/openapi.json", include_in_schema=False)
            async def openapi() -> dict[str, Any]:
                out: dict = get_openapi(
                    title=application.title,
                    version=application.version,
                    routes=application.routes,
                )

                return out

            application.include_router(docs_router)

    return application
