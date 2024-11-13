from typing import Annotated
from core.route import route
from fastapi import APIRouter, Body, Depends, status, Request, Response
from config import settings
from schemas.user_service.user import LoginForm
from apis.v1.deps import is_supper_admin


router = APIRouter()


@route(
    request_method=router.post,
    path="/login",
    status_code=status.HTTP_200_OK,
    payload_key="login_form",
    service_url=settings.USER_SERVICE_URL,
    authentication_required=False,
    post_processing_func="core.post_processing.access_token_generate_handler",
    response_model="schemas.user_service.user.LoginResponse",
)
async def login(
    login_form: Annotated[LoginForm, Body()], request: Request, response: Response
):
    pass


@route(
    request_method=router.post,
    path="/logout",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func="core.post_processing.revoke_token",
    authentication_token_decoder="core.security.decode_access_token",
    service_header_generator="core.security.generate_request_header",
)
async def logout(
    request: Request, response: Response, token=Depends(is_supper_admin)
):
    pass


