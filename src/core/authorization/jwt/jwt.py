from datetime import datetime, timedelta
from typing import Dict, Optional, Self
import jwt
from core.exception.auth_exception import (
    AuthTokenMissing,
    AuthTokenExpired,
    AuthTokenCorrupted,
)
from core.logging.logger import Logger
from config import settings
from core.authorization.store.whitelist import WhiteList
from core.authorization.jwt.certfile import CertFile
from core.authorization.jwt.interface import JWTInterface
from .constant import PUBLIC_KEY, PRIVATE_KEY, PEM_NAME
from core.db.redis.redis_pool import redis_pool

logger = Logger(__name__)


class JWTAuth(JWTInterface):
    def __init__(
        self,
        algorithm: str = "RS256",
    ):
        self._expire = 10  # in minutes
        self._algorithm = algorithm

        self.wl_token = WhiteList(redis_pool)
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
                key=self.wl_token.gen_key(
                    key=whitelist_key, uname=payload["payload"]["username"]
                ),
                key_hash=token,
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
        pem_name = f"{payload['uuid']}"

        encoded_jwt = jwt.encode(
            to_encode,
            self.certfile.set_pem_name(pem_name).read(PRIVATE_KEY),
            algorithm=self._algorithm,
            headers={PEM_NAME: pem_name},
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
        pem_name = decode_header.get(PEM_NAME)
        if not pem_name:
            raise AuthTokenCorrupted("Auth token is corrupted in headers.")

        try:
            return jwt.decode(
                token,
                self.certfile.set_pem_name(pem_name).read(PUBLIC_KEY),
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
