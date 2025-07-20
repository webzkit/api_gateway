from starlette.middleware.cors import CORSMiddleware
from typing import Any, Dict
from config import settings
from apis.v1.api import api_router
from core.setup import create_application

from opentelemetry.propagate import inject
from utils import PrometheusMiddleware, metrics, setting_otlp

from core.monitors.logger import Logger

logger = Logger(__name__)

# Init application
app = create_application(router=api_router, settings=settings)

# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=settings.APP_NAME)
app.add_route("/metrics", metrics)

# Setting openTelemetry exporter
setting_otlp(app, settings.APP_NAME, "tempo:4317")


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
async def root() -> Any:
    logger.error("Hello World")
    result: Dict[Any, Any] = {
        "message": f"Your {settings.APP_NAME} endpoint is working"
    }

    return result


@app.get("/health")
def health_status():
    return {"status": "healthy"}
