from starlette.middleware.cors import CORSMiddleware
from typing import Any, Dict

from config import settings
from apis.v1.api import api_router
from core.setup import create_application
from core.helpers.cache import use_cache


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


@app.get("/")
# @use_cache(key_prefix="test", expiration=1000)
async def root() -> Any:
    result: Dict[Any, Any] = {
        "message": f"Your {settings.APP_NAME} endpoint is working"
    }

    return result
