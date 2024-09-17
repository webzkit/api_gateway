from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from typing import Any, Dict

from config import settings

from routes.v1.api import api_router


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.APP_API_PREFIX}/openapi.json"
)

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

app.include_router(api_router, prefix=settings.APP_API_PREFIX)


@app.get("/")
def root(
) -> Any:
    result: Dict[Any, Any] = {
        "message": f"Your {settings.APP_NAME} endpoint is working"
    }

    return result
