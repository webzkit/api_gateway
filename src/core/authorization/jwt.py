from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from core.helpers.cache import has_whitelist_token
from core.exceptions import AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted
from core.helpers.utils import hashkey
from core.monitors.logger import Logger

# TODO generate key at Prod
from .define_key import PRIVATE_KEY, PUBLIC_KEY

logger = Logger(__name__)


class JWTAuth:
    def __init__(
        self,
        expire_minute: int = 10,
        algorithm: str = "RS256",
        public_key: str = PUBLIC_KEY,
        private_key: str = PRIVATE_KEY,
    ):
        self.__expire_minute = expire_minute
        self.__algorithm = algorithm
        self.__public_key = public_key
        self.__private_key = private_key

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
        try:
            payload = await self.__decode(token=token)

            username = payload["payload"]["username"]
            cache_key = f"whitelist_token:{username}:{whitelist_key}:{hashkey(token)}"

            if not await has_whitelist_token(cache_key):
                logger.debug(f"Token not found in cache: {cache_key}")
                raise AuthTokenExpired("Auth token is expired")

            return payload
        except Exception as e:
            raise Exception(f"{e}")

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
            to_encode, self.__private_key, algorithm=self.__algorithm
        )

        return encoded_jwt

    async def __decode(
        self,
        token: Optional[str] = None,
    ):
        if token is None:
            raise AuthTokenMissing("Auth token is missing in headers.")

        token = self.__replace_token_bearer(token)

        try:
            return jwt.decode(token, self.__public_key, algorithms=[self.__algorithm])
        except jwt.exceptions.ExpiredSignatureError as e:
            logger.debug(f"Token expired: {e}")

            raise AuthTokenExpired("Auth token is expired.")

        except jwt.exceptions.DecodeError as e:
            logger.debug(f"Token corrupted: {e}")

            raise AuthTokenCorrupted("Auth token is corrupted.")

    def __replace_token_bearer(self, token: str):
        return token.replace("Bearer ", "")
