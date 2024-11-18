from typing import Any
from fastapi import APIRouter, Request, Response, status

from config import settings
from core.route import route
from schemas.user_service.group import GroupCreate, GroupUpdate


router = APIRouter()


@route(
    request_method=router.get,
    path="",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    authentication_token_decoder="core.security.decode_access_token",
    service_authorization_checker="core.security.is_admin_user",
    service_header_generator="core.security.generate_request_header",
    response_model=None,
    response_list=True,
)
async def gets(
    request: Request,
    response: Response,
    page: int = 1,
    items_per_page: int = 100,
) -> Any:
    pass


@route(
    request_method=router.get,
    path="/{id}",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    authentication_token_decoder="core.security.decode_access_token",
    service_authorization_checker="core.security.is_admin_user",
    service_header_generator="core.security.generate_request_header",
    response_model=None,
    response_list=False,
)
async def get(id: int, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.post,
    path="",
    status_code=status.HTTP_201_CREATED,
    payload_key="user",
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    authentication_token_decoder="core.security.decode_access_token",
    service_authorization_checker="core.security.is_admin_user",
    service_header_generator="core.security.generate_request_header",
)
async def create(user: GroupCreate, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.put,
    path="/{id}",
    status_code=status.HTTP_200_OK,
    payload_key="user",
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    authentication_token_decoder="core.security.decode_access_token",
    service_authorization_checker="core.security.is_admin_user",
    service_header_generator="core.security.generate_request_header",
)
async def update(
    id: int, user: GroupUpdate, request: Request, response: Response
) -> Any:
    pass


@route(
    request_method=router.delete,
    path="/soft/{id}",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    authentication_token_decoder="core.security.decode_access_token",
    service_authorization_checker="core.security.is_admin_user",
    service_header_generator="core.security.generate_request_header",
)
async def delete(id: int, request: Request, response: Response) -> Any:
    pass
