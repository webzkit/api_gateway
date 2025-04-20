from fastapi.responses import JSONResponse
from config import settings
from core.authorization.store.whitelist import WhiteList
from core.authorization.constans import REFRESH_TOKEN, ACCESS_TOKEN
from core.db.cache_redis import cache
from core.authorization.store.blacklist import BlackList
from core.authorization.schema import (
    BlackListTokenSchema,
    WhiteListTokenSchema,
)
from core.authorization.jwt.jwt import JWTAuth
from urllib.parse import urlencode
from typing import Optional, Dict


class Authorize(JWTAuth):
    SCOPE_SUPER_ADMIN = ["Supper Admin"]

    def __init__(
        self,
        algorithm: str = "RS256",
    ):
        self._payload = {}
        self._token = ""
        JWTAuth.__init__(self, algorithm=algorithm)
        self.wl_token = WhiteList(cache)
        self.bl_token = BlackList(cache)

    async def handle_refresh(self):
        payload = await self.verify(token=self.get_token(), whitelist_key=REFRESH_TOKEN)

        # Destroy old refresh token
        uname = payload["payload"]["username"]
        await self.wl_token.destroy(
            key=self.wl_token.gen_key(key=REFRESH_TOKEN, uname=uname),
            key_hash=f"{self.get_token()}",
        )

        access_token = (
            await self.set_payload(payload.get("payload"))
            .set_exprire(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            .encrypt(self.get_payload())
        )
        refresh_token = await self.set_exprire(
            settings.REFRESH_TOKEN_EXPIRE_MINUTES
        ).encrypt(self.get_payload())

        data = {
            ACCESS_TOKEN: access_token,
            REFRESH_TOKEN: refresh_token,
            "token_type": "bearer",
        }

        if settings.TOKEN_VERIFY_BACKEND:
            await self._set_to_whitelist(data=WhiteListTokenSchema(**data))
            await self._set_to_blacklist(data=BlackListTokenSchema(**data))

        response = JSONResponse(content=data)

        if settings.USE_COOKIE_AUTH:
            await self._set_cookie(
                response,
                key=REFRESH_TOKEN,
                value=refresh_token,
                expire=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            )

        return response

    async def handle_logout(self, token: str):
        payload = await self.verify(token)
        username = payload["payload"]["username"]

        await self.wl_token.destroy(
            key=self.wl_token.gen_key(key=ACCESS_TOKEN, uname=username),
            key_hash=token,
        )

    async def handle_login(self):
        access_token = await self.set_exprire(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ).encrypt(self.get_payload())
        refresh_token = await self.set_exprire(
            settings.REFRESH_TOKEN_EXPIRE_MINUTES
        ).encrypt(self.get_payload())

        data = {
            ACCESS_TOKEN: access_token,
            REFRESH_TOKEN: refresh_token,
            "token_type": "bearer",
        }

        if settings.TOKEN_VERIFY_BACKEND:
            await self._set_to_whitelist(data=WhiteListTokenSchema(**data))

        response = JSONResponse(content=data)

        if settings.USE_COOKIE_AUTH:
            await self._set_cookie(
                response,
                key=REFRESH_TOKEN,
                value=refresh_token,
                expire=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            )

        return response

    async def _set_to_whitelist(self, data: WhiteListTokenSchema):
        ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        for k, v in data.to_dict().items():
            if k == "refresh_token":
                ttl = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60

            await self.wl_token.set_ttl(ttl).create(
                key=self.wl_token.get_key_by(
                    key=self.wl_token.gen_key(
                        key=k, uname=self.get_payload_by("username")
                    ),
                    key_hash=v,
                ),
                value=data.to_dict(),
            )

    async def _set_to_blacklist(self, data: BlackListTokenSchema):
        for k, v in data.to_dict().items():
            ttl = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60

            await self.bl_token.set_ttl(ttl).create(
                key=self.bl_token.get_key_by(
                    key=self.bl_token.gen_key(
                        key=k, uname=self.get_payload_by("username")
                    ),
                    key_hash=v,
                ),
                value=data.to_dict(),
            )

    async def _set_cookie(
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

    def set_payload(self, payload: Dict = {}):
        self._payload = payload

        return self

    def get_payload(self):
        if "payload" in self._payload:
            return self._payload["payload"]

        return self._payload

    def set_token(self, token: Optional[str] = None):
        self._token = token

        return self

    def get_token(self):
        return self._token

    def generate_request_init_data(self):
        return {
            "request-init-data": urlencode(self._payload),
            "Authorization": self.get_token(),
        }

    def is_admin(self):
        return self._get_scope() in self.SCOPE_SUPER_ADMIN

    def get_payload_by(self, key: str, default: str = "") -> str:
        payload = self.get_payload()
        if not payload:
            return default

        return payload.get(key, default)

    def _get_scope(self):
        return self.get_payload()["group"]["name"]
