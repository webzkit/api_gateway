from fastapi import APIRouter

from .user_service import authenticate, user, group


api_router = APIRouter()


api_router.include_router(
    authenticate.router, prefix="/authenticate", tags=["Authorization"]
)

api_router.include_router(
    user.router, prefix="/users", tags=["User"]
)

api_router.include_router(
    group.router, prefix="/groups", tags=["User Group"]
)
