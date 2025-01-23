from typing import Any
from fastapi import APIRouter, Request, Response, status

from config import settings
from core.route import route
from schemas.avatar_service.geographies.province import (
    ProvinceGeographyCreate as Create,
    ProvinceGeographyUpdate as Update,
)

router = APIRouter()

SERVICE_URL = settings.AVATAR_SERVICE_URL


@route(
    request_method=router.get,
    path="",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    response_model=None,
    response_list=True,
    # cache_key_prefix="avatar:geography:province:results:items_per_page_{items_per_page}:page_{page}",
    # cache_resource_id_name="page",
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
    service_url=SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    response_model=None,
    response_list=False,
    cache_key_prefix="avatar:geography:province:result",
    cache_resource_id_type=int,
)
async def get(id: int, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.post,
    path="",
    status_code=status.HTTP_201_CREATED,
    payload_key="create",
    service_url=SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
)
async def create(create: Create, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.put,
    path="/{id}",
    status_code=status.HTTP_200_OK,
    payload_key="update",
    service_url=SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    cache_key_prefix="avatar:geography:province:result",
    cache_resource_id_type=int,
)
async def update(id: int, update: Update, request: Request, response: Response) -> Any:
    pass


@route(
    request_method=router.delete,
    path="/soft/{id}",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    cache_key_prefix="avatar:geography:province:result",
    cache_resource_id_type=int,
)
async def delete(id: int, request: Request, response: Response) -> Any:
    pass
