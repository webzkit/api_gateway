from typing import Optional

from fastapi.responses import JSONResponse
from core.authorization.authenticate import Authorization
from core.authorization.jwt import JWTAuth
from config import settings
from core.authorization.whitelist import WhiteList
from core.authorization.constans import REFRESH_TOKEN, ACCESS_TOKEN

from core.db.cache_redis import cache


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

        self.wl_token = WhiteList(cache)

    async def handle_refresh(self, token: Optional[str] = None):
        payload = await self.verify(token=token, whitelist_key=REFRESH_TOKEN)

        return await self.set_payload(payload.get("payload")).handle_login()

    async def handle_logout(self, token: str):
        payload = await self.verify(token)
        username = payload["payload"]["username"]

        await self.wl_token.revoke_all(key=f"{ACCESS_TOKEN}:{username}", value=token)

    async def handle_login(self):
        access_token = self.encrypt(self.get_payload())
        refresh_token = self.set_exprire(settings.REFRESH_TOKEN_EXPIRE_MINUTES).encrypt(
            self.get_payload()
        )

        data = {
            ACCESS_TOKEN: access_token,
            REFRESH_TOKEN: refresh_token,
            "token_type": "bearer",
        }

        if settings.TOKEN_VERIFY_BACKEND:
            await self.wl_token.set_ttl(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ).create(
                key=self.wl_token.gen_key_by(
                    key=f"{ACCESS_TOKEN}:{self.get_payload_by('username')}",
                    key_hash=access_token,
                ),
                value=data,
            )

            await self.wl_token.set_ttl(
                settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
            ).create(
                key=self.wl_token.gen_key_by(
                    key=f"{REFRESH_TOKEN}:{self.get_payload_by('username')}",
                    key_hash=refresh_token,
                ),
                value=data,
            )

        response = JSONResponse(content=data)

        if settings.USE_COOKIE_AUTH:
            await self.set_cookie(
                response,
                key=REFRESH_TOKEN,
                value=refresh_token,
                expire=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
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

    async def set_cookie(
        self, response: JSONResponse, key: str, value: str, expire: int = 60
    ):
        response.set_cookie(
            key=key,
            value=value,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=expire * 60,  # convert to secons
        )
