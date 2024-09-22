from typing import Any
from fastapi import APIRouter, Request, Response, status

from config import settings
from core.route import route


router = APIRouter()


@route(
    request_method=router.get,
    path="",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func=None,
    authentication_token_decoder='core.security.decode_access_token',
    service_authorization_checker='core.security.is_admin_user',
    service_header_generator='core.security.generate_request_header',
    response_model="schemas.UserResponse",
    response_list=True
)
async def gets(request: Request, response: Response) -> Any:
    pass
