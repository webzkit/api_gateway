from datetime import datetime, timedelta
from typing import Dict, Optional, Self
import jwt
from core.exception.auth_exception import (
    AuthTokenMissing,
    AuthTokenExpired,
    AuthTokenCorrupted,
)
from core.monitors.logger import Logger
from config import settings
from core.authorization.store.whitelist import WhiteList
from core.authorization.jwt.certfile import CertFile
from core.db.cache_redis import cache
from core.authorization.jwt.interface import JWTInterface
from .constant import PUBLIC, PRIVATE


logger = Logger(__name__)


class JWTAuth(JWTInterface):
    def __init__(
        self,
        expire: int = 10,
        algorithm: str = "RS256",
    ):
        self._expire = expire
        self._algorithm = algorithm

        self.wl_token = WhiteList(cache)
        self.certfile = CertFile()

    async def encrypt(self, payload: Dict):
        return self._encode(payload)

    async def decrypt(self, token: Optional[str] = None):
        return await self._decode(token=token)

    async def verify(
        self, token: Optional[str] = None, whitelist_key: str = "access_token"
    ):
        if token is None:
            raise AuthTokenMissing("Auth token is missing in headers.")

        token = self._replace_token(token)
        payload = await self._decode(token=token)

        if settings.TOKEN_VERIFY_BACKEND:
            verified = await self.wl_token.has(
                key=f"{whitelist_key}:{payload['payload']['username']}", key_hash=token
            )

            if verified is False:
                raise AuthTokenExpired("Auth token is expired")

        return payload

    def set_exprire(self, expire: int) -> Self:
        self._expire = expire

        return self

    def get_expire(self):
        return datetime.now().replace(tzinfo=None) + timedelta(minutes=self._expire)

    def _encode(self, payload: Dict):
        to_encode = {"payload": payload, "exp": self.get_expire()}

        encoded_jwt = jwt.encode(
            to_encode,
            self.certfile.set_username(payload["username"]).read(PRIVATE),
            algorithm=self._algorithm,
            headers={"kid": "info"},
        )

        return encoded_jwt

    async def _decode(
        self,
        token: Optional[str] = None,
    ):
        if token is None:
            raise AuthTokenMissing("Auth token is missing in headers.")

        token = self._replace_token(token)
        decode_header = jwt.get_unverified_header(token)
        username_header = decode_header.get("kid")
        if not username_header:
            raise AuthTokenCorrupted("Auth token is corrupted.")

        try:
            return jwt.decode(
                token,
                self.certfile.set_username(username_header).read(PUBLIC),
                algorithms=[self._algorithm],
            )
        except jwt.exceptions.ExpiredSignatureError as e:
            logger.debug(f"Token expired: {e}")

            raise AuthTokenExpired("Auth token is expired.")

        except jwt.exceptions.DecodeError as e:
            logger.debug(f"Token corrupted: {e}")

            raise AuthTokenCorrupted("Auth token is corrupted.")

    def _replace_token(self, token: str):
        return token.replace("Bearer ", "")
