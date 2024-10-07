from typing import Annotated
from core.route import route
from fastapi import APIRouter, Body, status, Request, Response
from config import settings
from schemas import LoginForm


router = APIRouter()


@route(
    request_method=router.post,
    path="/login",
    status_code=status.HTTP_200_OK,
    payload_key="login_form",
    service_url=settings.USER_SERVICE_URL,
    authentication_required=False,
    post_processing_func="core.post_processing.access_token_generate_handler",
    response_model="schemas.LoginResponse",
)
async def login(
    login_form: Annotated[LoginForm, Body()], request: Request, response: Response
):
    pass
