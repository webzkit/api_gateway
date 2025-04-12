from typing import Optional

from fastapi.responses import JSONResponse
from core.authorization.authenticate import Authorization
from core.authorization.jwt import JWTAuth
from config import settings
from core.authorization.whitelist import WhiteList


class Authorize(JWTAuth, Authorization):
    def __init__(
        self,
        expire_minute: int = 10,
        algorithm: str = "RS256",
    ):
        JWTAuth.__init__(
            self,
            expire_minute=expire_minute,
            algorithm=algorithm,
        )

        self.wl_token = WhiteList()

    async def handle_refresh(self, token: Optional[str] = None):
        payload = await self.verify(token=token, whitelist_key="refresh_token")

        return await self.set_payload(payload.get("payload")).handle_login()

    async def handle_logout(self, token: Optional[str] = None):
        payload = await self.verify(token)
        await self.wl_token.set_username(payload["payload"]["username"]).revoke_all(
            key="access_token", token=token
        )

    async def handle_login(self):
        access_token = self.encrypt(self.get_payload())
        refresh_token = self.set_exprire(settings.REFRESH_TOKEN_EXPIRE_MINUTES).encrypt(
            self.get_payload()
        )

        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

        if settings.TOKEN_VERIFY_BACKEND:

            self.wl_token.set_payload(data).set_username(
                self.get_payload_by("username", "")
            )

            await self.wl_token.set_expire(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ).store_access_token()

            await self.wl_token.set_expire(
                settings.REFRESH_TOKEN_EXPIRE_MINUTES
            ).store_refresh_token()

        response = JSONResponse(content=data)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )

        return response

    async def get_by(self, key: str):
        user = await self.user()
        if not user:
            return ""

        return user.get(key)

    async def user(self):
        payload = await self.decrypt(token=self.get_token_bearer())

        return self.set_payload(payload).get_payload()

    def get_payload_by(self, key: str, default: str = "") -> str:
        user = self.get_payload()
        if not user:
            return default

        return user.get(key, default)
