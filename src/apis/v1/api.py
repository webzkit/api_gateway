from fastapi import APIRouter, Depends

from config import AppSetting, EnviromentOption, settings
from apis.v1.deps import use_author_for_dev

from .user_service import authenticate, user, group

from .avatar_service.geographies import province, district, ward

api_router = APIRouter()
api_router.include_router(
    authenticate.router, prefix="/authenticate", tags=["Authorization"]
)

# TODO
# Removed at prod
if isinstance(settings, AppSetting):
    if settings.APP_ENV == EnviromentOption.DEVELOPMENT.value:
        api_router.dependencies = [Depends(dependency=use_author_for_dev)]

# Register engine service
api_router.include_router(user.router, prefix="/users", tags=["User"])
api_router.include_router(group.router, prefix="/groups", tags=["User Group"])


# Register avatar service
api_router.include_router(
    province.router, prefix="/geographies/provinces", tags=["Geography Province"]
)
api_router.include_router(
    district.router, prefix="/geographies/districts", tags=["Geography District"]
)
api_router.include_router(
    ward.router, prefix="/geographies/wards", tags=["Geography Ward"]
)
