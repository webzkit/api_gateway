from fastapi.responses import JSONResponse
from config import settings
from core.authorization.store.whitelist import WhiteList
from core.authorization.constans import REFRESH_TOKEN, ACCESS_TOKEN
from core.db.cache_redis import cache
from core.authorization.store.blacklist import BlackList
from core.authorization.schema import TOKEN_BACKEND
from core.authorization.jwt.jwt import JWTAuth
from urllib.parse import urlencode
from typing import Optional, Dict


class Authorize(JWTAuth):
    SCOPE_SUPER_ADMIN = ["Supper Admin"]

    def __init__(
        self,
        expire: int = 10,
        algorithm: str = "RS256",
    ):
        self._payload = {}
        self._token = ""
        JWTAuth.__init__(self, expire=expire, algorithm=algorithm)
        self.wl_token = WhiteList(cache)
        self.bl_token = BlackList(cache)

    async def handle_refresh(self):
        payload = await self.verify(token=self.get_token(), whitelist_key=REFRESH_TOKEN)

        uname = payload["payload"]["username"]
        await self.wl_token.destroy(
            key=f"{REFRESH_TOKEN}:{uname}", key_hash=f"{self.get_token()}"
        )

        # TODO store to blacklist

        access_token = await self.set_payload(payload.get("payload")).encrypt(
            self.get_payload()
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
            await self._set_to_whitelist(data=TOKEN_BACKEND(**data))

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

        await self.wl_token.destroy(key=f"{ACCESS_TOKEN}:{username}", key_hash=token)

    async def handle_login(self):
        access_token = await self.encrypt(self.get_payload())
        refresh_token = await self.set_exprire(
            settings.REFRESH_TOKEN_EXPIRE_MINUTES
        ).encrypt(self.get_payload())

        data = {
            ACCESS_TOKEN: access_token,
            REFRESH_TOKEN: refresh_token,
            "token_type": "bearer",
        }

        if settings.TOKEN_VERIFY_BACKEND:
            await self._set_to_whitelist(data=TOKEN_BACKEND(**data))

        response = JSONResponse(content=data)

        if settings.USE_COOKIE_AUTH:
            await self._set_cookie(
                response,
                key=REFRESH_TOKEN,
                value=refresh_token,
                expire=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            )

        return response

    async def _set_to_whitelist(self, data: TOKEN_BACKEND):
        ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        for k, v in data.to_dict().items():
            if k == "token_type":
                continue

            if k == "refresh_token":
                ttl = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60

            await self.wl_token.set_ttl(ttl).create(
                key=self.wl_token.get_key_by(
                    key=f"{k}:{self.get_payload_by('username')}",
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

    async def get_by(self, key: str):
        user = await self.user()
        if not user:
            return ""

        return user.get(key)

    async def user(self):
        payload = await self.decrypt(token=self.get_token())

        return self.set_payload(payload).get_payload()

    def get_payload_by(self, key: str, default: str = "") -> str:
        user = self.get_payload()
        if not user:
            return default

        return user.get(key, default)

    def _get_scope(self):
        return self.get_payload()["group"]["name"]
