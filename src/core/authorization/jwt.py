from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from core.exception.auth_exception import (
    AuthTokenMissing,
    AuthTokenExpired,
    AuthTokenCorrupted,
)
from core.monitors.logger import Logger
from config import settings
from core.authorization.whitelist import WhiteList
from core.authorization.certfile import CertFile
from core.db.cache_redis import cache


logger = Logger(__name__)


class JWTAuth:
    def __init__(
        self,
        expire_minute: int = 10,
        algorithm: str = "RS256",
    ):
        self.__expire_minute = expire_minute
        self.__algorithm = algorithm

        self.wl_token = WhiteList(cache)
        self.certfile = CertFile()

    def encrypt(self, payload: Dict):
        return self.__encode(payload)

    async def decrypt(self, token: Optional[str] = None):
        return await self.__decode(token=token)

    async def verify(
        self, token: Optional[str] = None, whitelist_key: str = "access_token"
    ):
        if token is None:
            raise AuthTokenMissing("Auth token is missing in headers.")

        token = self.__replace_token_bearer(token)
        payload = await self.__decode(token=token)

        if settings.TOKEN_VERIFY_BACKEND:
            verified = await self.wl_token.has_whitelist(
                key=f"{whitelist_key}:{payload['payload']['username']}", key_hash=token
            )

            if verified is False:
                raise AuthTokenExpired("Auth token is expired")

        return payload

    def set_exprire(self, expire_minute: int):
        self.__expire_minute = expire_minute

        return self

    def get_expire(self):
        return datetime.now().replace(tzinfo=None) + timedelta(
            minutes=self.__expire_minute
        )

    def __encode(self, payload: Dict):
        to_encode = {"payload": payload, "exp": self.get_expire()}

        encoded_jwt = jwt.encode(
            to_encode,
            self.certfile.set_username(payload["username"]).read("private"),
            algorithm=self.__algorithm,
            headers={"kid": "info"},
        )

        return encoded_jwt

    async def __decode(
        self,
        token: Optional[str] = None,
    ):
        if token is None:
            raise AuthTokenMissing("Auth token is missing in headers.")

        token = self.__replace_token_bearer(token)
        decode_header = jwt.get_unverified_header(token)
        username_header = decode_header.get("kid")
        if not username_header:
            raise AuthTokenCorrupted("Auth token is corrupted.")

        try:
            return jwt.decode(
                token,
                self.certfile.set_username(username_header).read("public"),
                algorithms=[self.__algorithm],
            )
        except jwt.exceptions.ExpiredSignatureError as e:
            logger.debug(f"Token expired: {e}")

            raise AuthTokenExpired("Auth token is expired.")

        except jwt.exceptions.DecodeError as e:
            logger.debug(f"Token corrupted: {e}")

            raise AuthTokenCorrupted("Auth token is corrupted.")

    def __replace_token_bearer(self, token: str):
        return token.replace("Bearer ", "")
