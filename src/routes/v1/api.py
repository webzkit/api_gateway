from fastapi import APIRouter

from .endpoints import authenticate


api_router = APIRouter()
api_router.include_router(
    authenticate.router, prefix="/authenticate", tags=["Authorization"])
