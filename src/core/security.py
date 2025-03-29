from datetime import datetime, timedelta
from typing import Dict, Optional, Union
import jwt
from urllib.parse import urlencode
from passlib.context import CryptContext
from core.exceptions import AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted
from core.helpers.cache import has_whitelist_token
from core.helpers.utils import hashkey
from core.monitors.logger import Logger
from config import settings

logger = Logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "RS256"

PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwpz38WQsUM+O4aZqVd8kvtUk9leeW/A3VQY2StzKt1FQ9CSU
8lCv+7T81e1dlMgCy0ZQVpXGmAf79TBKt4vaeSM/HK0TBifBHiOtwS3cGho+XV9/
9Zl/tJi3E+ykEaOSlufCRpJqPkwypiXKRfdcg6muoeAxDRCleNzpCvFVze++IQ4M
zR5rQ17UsSVsFHjWMw/lisf4mE1MWlE4FmSe7rktHlDEx/neZTI6nrKdk8XYJvfc
DBqq6hRabk+swVZ8GeQE7kuby6IBHc3kKCVyRxDkMVyImPLuIooQLkWivZYkGnc9
ylc4vQw+iAtD0psLE3whQAtHJdfxTp2vowqixwIDAQABAoIBAQCayTgXQWJR39O3
u6GlrPZP5b0hRW0JmNSZhnhWMKf3B/EITbQ9ylk+LKRQDhu5Qx+dx84MH9I1h1wp
loBG3jAk2xjOWQXhhmr96si+9heylx71KwjeMXk2DaTHbxbLhLsJ1Ula0gc4h2hd
Z38rCOQHQEVKMMMyrgO+To34Cx0AzgIvsYbkRSzk6N3/3Y6Q9fcdz8sNZzWZbobc
runGeTAjcg2gEvcO8F2KkiZse4DM0ERPb3Y5F/abuGDrhl1xKvjP7RmkMIZa4na/
TA3KXVyrMsZyXV+ggSNa3pUZOg0IXzyOr2H0DMtf0/3r7YCl2+oJ5FOJXm7c6iUU
CRTfw8yxAoGBAPZ1MJVS/KvaJAI36QSYPM5YyrbzsOrXx+dAP3ire3BUqPwN2w5I
WIbYtKZqJemADodN/9SjKJJHmEGSw+kq0PMjXp1hnFmJK7rRUlbKgR1yTN6mZRk4
GAMgUyHIneRxa3lJ6oP28aEQqEf5vbJ5TpAkV5UuhPervoay76QNJklPAoGBAMol
6V5msBITwBH/TRSvAm+R5zIXSaULpe4/f81ZV+saZNFCbxtIgQnHdO9jxZgdl6Hx
o6jvGyBfG2pj3J5Rkfw02bkrJVzGB+uPLbzThYDPDT2ZciNoD6aokIXWSiNekWCD
LYcPjSQPHDIo0b80Hh+L0gGXfVJabm46Eo4LW0EJAoGBAJ7GntcEkK1yKpKXTHJe
VYYmY+p7knWpMCsGFB38c9jJYdiIYKCR8R5mi/NOHUCR9Eos8O0fc+rRXwCXuckE
gXqyRakkkmKIYXjIk8BAU/ARi/5Auo8FuUqCT6xLH5VlkHSiLwh3VfGK1q8P8KsD
RZ7NGvOL9bPNnEARFRveMNU3AoGAXFDN71+D3u2IFG/72otF2H/QDk8WQbo9D72N
9tBrVyGZkvr81H/a9gVRgJWWwi4ZdkpszBRN1g247nAma2KjAYN9PpPWnzSMn2Wm
pIoQeM+Vo2D0//hg1WI7hfNjrh1c1K9zVi+i7Cm+XaXIi8IYU529zR5KjBZiQhJh
MN880EkCgYAznSTuiFTwcKvWhZKt7F0c3eXZJ3s2keB35teTyW4ZER2ilzJq68s4
4O09Xvw2gtbMsKel4KY2tmkkv/SaHwvwGEVjC6+C0wvZgSyXLqDzTgYRVNcu9FjN
B/mXfMqh8eoc+B5hOhia3hgPvqMzj35a4UD3hox52KskuikH4QuX3w==
-----END RSA PRIVATE KEY-----
"""
PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwpz38WQsUM+O4aZqVd8k
vtUk9leeW/A3VQY2StzKt1FQ9CSU8lCv+7T81e1dlMgCy0ZQVpXGmAf79TBKt4va
eSM/HK0TBifBHiOtwS3cGho+XV9/9Zl/tJi3E+ykEaOSlufCRpJqPkwypiXKRfdc
g6muoeAxDRCleNzpCvFVze++IQ4MzR5rQ17UsSVsFHjWMw/lisf4mE1MWlE4FmSe
7rktHlDEx/neZTI6nrKdk8XYJvfcDBqq6hRabk+swVZ8GeQE7kuby6IBHc3kKCVy
RxDkMVyImPLuIooQLkWivZYkGnc9ylc4vQw+iAtD0psLE3whQAtHJdfxTp2vowqi
xwIDAQAB
-----END PUBLIC KEY-----
"""


class JWTAuth:
    def __init__(
        self,
        expire_minute: int = 10,
        algorithm: str = "RS256",
        public_key: str = PUBLIC_KEY,
        private_key: str = PRIVATE_KEY,
    ):
        self.expire_minute = expire_minute
        self.algorithm = algorithm
        self.public_key = public_key
        self.private_key = private_key

    def encrypt(self, payload: Dict):
        return self.__encode(payload)

    def set_exprire(self, expire_minute: int):
        self.expire_minute = expire_minute

        return self

    def get_expire(self):
        return datetime.now().replace(tzinfo=None) + timedelta(
            minutes=self.expire_minute
        )

    def __encode(self, payload: Dict):
        to_encode = {"payload": payload, "exp": self.get_expire()}
        encoded_jwt = jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)

        return encoded_jwt

    async def decrypt(self, token: Optional[str] = None):
        return await self.__decode(token=token)

    async def __decode(
        self,
        token: Optional[str] = None,
        use_for: str = "access_token",
        is_verify: bool = True,
    ):
        if token is None:
            raise AuthTokenMissing("Auth token is missing in headers.")

        token_bearer = token.replace("Bearer ", "")
        try:
            payload = jwt.decode(
                token_bearer, self.public_key, algorithms=[self.algorithm]
            )

            # verify token internal
            if is_verify:
                username = payload["payload"]["username"]
                cache_key = (
                    f"whitelist_token:{username}:{use_for}:{hashkey(token_bearer)}"
                )
                if not await verify_token_internal(cache_key):
                    logger.debug(f"Token not found in cache: {cache_key}")
                    raise AuthTokenExpired("Auth token is expired")

            return payload

        except jwt.exceptions.ExpiredSignatureError as e:
            logger.debug(f"Token expired: {e}")

            raise AuthTokenExpired("Auth token is expired.")

        except jwt.exceptions.DecodeError as e:
            logger.debug(f"Token corrupted: {e}")

            raise AuthTokenCorrupted("Auth token is corrupted.")


jwt_auth = JWTAuth(expire_minute=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


async def test_decode_access_token(
    token: Optional[str] = None, use_for: str = "access_token", is_verify: bool = True
):
    return await jwt_auth.decrypt(token=token)


def encode_access_token(payload: Dict, expire_minute: int = 10):
    expire = datetime.now().replace(tzinfo=None) + timedelta(minutes=expire_minute)
    to_encode = {"payload": payload.get("data"), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    pwd_context.schemes()

    return pwd_context.hash(password)


async def decode_access_token(
    authorization: Union[str, None] = None,
    use_for: str = "access_token",
    is_verify: bool = True,
):
    if not authorization:
        raise AuthTokenMissing("Auth token is missing in headers.")

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])

        # verify token internal
        if is_verify:
            username = payload["payload"]["username"]
            cache_key = f"whitelist_token:{username}:{use_for}:{hashkey(token)}"
            if not await verify_token_internal(cache_key):
                raise AuthTokenExpired("Auth token is expired")

        return payload

    except jwt.exceptions.ExpiredSignatureError:
        raise AuthTokenExpired("Auth token is expired.")

    except jwt.exceptions.DecodeError:
        raise AuthTokenCorrupted("Auth token is corrupted.")


async def verify_token_internal(cache_key: str) -> bool:
    return await has_whitelist_token(cache_key)


def generate_request_header(token_payload, token_bearer: Optional[str] = None):
    return {
        "request-init-data": urlencode(token_payload.get("payload")),
        "Authorization": token_bearer,
    }


def is_admin_user(token_payload):
    scope = token_payload.get("payload")["group"]["name"]
    return scope == "Supper Admin"


def is_default_user(token_payload):
    return token_payload["user_type"] in ["default", "admin"]


async def get_current_user_by(access_token: Optional[str] = None):
    if access_token is None:
        return None

    try:
        payload = await decode_access_token(authorization=access_token, is_verify=False)
        return payload["payload"]
    except Exception as error:
        logger.error(f"User not found by key {error}")

        return None
