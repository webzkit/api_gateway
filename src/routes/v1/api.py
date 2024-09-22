from fastapi import APIRouter

from .endpoints import authenticate
from .endpoints import user


api_router = APIRouter()


api_router.include_router(
    authenticate.router, prefix="/authenticate", tags=["Authorization"])

api_router.include_router(
    user.router, prefix="/users", tags=["User"]
)
