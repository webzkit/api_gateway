from fastapi import APIRouter, Depends

from config import AppSetting, EnviromentOption, settings
from apis.v1.deps import use_author_for_dev

from .user_service import authenticate, user, group, me

from .avatar_service.geographies import country, province, district, ward
from .avatar_service import sector, avatar

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
api_router.include_router(me.router, prefix="/me", tags=["Me"])


# Register avatar service
api_router.include_router(
    country.router, prefix="/geographies/countries", tags=["Geography Country"]
)

api_router.include_router(
    province.router, prefix="/geographies/provinces", tags=["Geography Province"]
)

api_router.include_router(
    district.router, prefix="/geographies/districts", tags=["Geography District"]
)

api_router.include_router(
    ward.router, prefix="/geographies/wards", tags=["Geography Ward"]
)

api_router.include_router(sector.router, prefix="/sectors", tags=["Avatar Sector"])

api_router.include_router(avatar.router, prefix="/avatars", tags=["Avatar"])
