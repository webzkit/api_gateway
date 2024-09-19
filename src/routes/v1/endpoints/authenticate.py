from core.route import route
from fastapi import APIRouter,  status, Request, Response
from config import settings
from schemas import LoginForm


router = APIRouter()


@route(
    request_method=router.post,
    path='/login',
    status_code=status.HTTP_201_CREATED,
    payload_key='username_password',
    service_url=settings.USERS_SERVICE_URL,
    authentication_required=False,
    post_processing_func='core.post_processing.access_token_generate_handler',
    response_model="schemas.LoginResponse"
)
async def login(username_password: LoginForm,
                request: Request, response: Response):
    pass
