from fastapi import FastAPI, status, Request, Response
from starlette.middleware.cors import CORSMiddleware
from typing import Any, Dict

from config import settings
from routes.v1.api import api_router

from core.route import route
from schemas import LoginForm, LoginResponse

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


@route(
    request_method=app.post,
    path='/api/login',
    status_code=status.HTTP_201_CREATED,
    payload_key='username_password',
    service_url=settings.USERS_SERVICE_URL,
    authentication_required=False,
    post_processing_func='core.post_processing.access_token_generate_handler',
    response_model='schemas.LoginResponse'
)
async def login(username_password: LoginForm,
                request: Request, response: Response):
    pass
