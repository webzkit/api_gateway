from fastapi import APIRouter, Depends

from config import AppSetting, EnviromentOption, settings
from apis.v1.deps import is_supper_admin

from .user_service import authenticate, user, group


api_router = APIRouter()
api_router.include_router(
    authenticate.router, prefix="/authenticate", tags=["Authorization"]
)

# TODO
# removed at prod
if isinstance(settings, AppSetting):
    if settings.APP_ENV != EnviromentOption.PRODUCTION.value:
        api_router.dependencies=[Depends(dependency=is_supper_admin)]


api_router.include_router(
    user.router, prefix="/users", tags=["User"]
)

api_router.include_router(
    group.router, prefix="/groups", tags=["User Group"]
)
