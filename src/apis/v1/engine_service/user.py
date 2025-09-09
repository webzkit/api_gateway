from typing import Any
from fastapi import APIRouter, Request, Response, status

from config import settings
from core.route import route
from schemas.engine_service.user import UserCreate, UserUpdate


router = APIRouter()

SERVICE_NAME = settings.ENGINE_SERVICE_NAME


@route(
    request_method=router.get,
    path="",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_name=SERVICE_NAME,
    authentication_required=True,
    post_processing_func=None,
    response_list=True,
    cache_key_prefix="users:results:items_per_page_{items_per_page}:page_{page}",
    cache_resource_id_name="page",
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
    service_name=SERVICE_NAME,
    authentication_required=True,
    post_processing_func=None,
    response_list=False,
    cache_key_prefix="users:result",
    cache_resource_id_type=int,
)
async def get(id: int, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.post,
    path="",
    status_code=status.HTTP_201_CREATED,
    payload_key="user",
    service_name=SERVICE_NAME,
    authentication_required=True,
    post_processing_func=None,
)
async def create(user: UserCreate, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.put,
    path="/{id}",
    status_code=status.HTTP_200_OK,
    payload_key="user",
    service_name=SERVICE_NAME,
    authentication_required=True,
    post_processing_func=None,
    cache_key_prefix="users:result",
    cache_resource_id_type=int,
)
async def update(
    id: int, user: UserUpdate, request: Request, response: Response
) -> Any:
    pass


@route(
    request_method=router.delete,
    path="/soft/{id}",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_name=SERVICE_NAME,
    authentication_required=True,
    post_processing_func=None,
    cache_key_prefix="users:result",
    cache_resource_id_type=int,
)
async def delete(id: int, request: Request, response: Response) -> Any:
    pass
