from datetime import datetime, timedelta
from typing import Dict, Union
import jwt
from urllib.parse import urlencode
from passlib.context import CryptContext
from core.exceptions import AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted


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


def encode_access_token(payload: Dict, expire_minute: int = 10):
    expire = datetime.now() + timedelta(minutes=expire_minute)
    print(payload.get("data"))
    to_encode = {"payload": payload.get("data"), "exp": expire}

    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    pwd_context.schemes()

    return pwd_context.hash(password)


def decode_access_token(authorization: Union[str, None] = None):
    if not authorization:
        raise AuthTokenMissing("Auth token is missing in headers.")

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])

        return payload

    except jwt.exceptions.ExpiredSignatureError:
        raise AuthTokenExpired("Auth token is expired.")

    except jwt.exceptions.DecodeError:
        raise AuthTokenCorrupted("Auth token is corrupted.")


def generate_request_header(token_payload):
    return {"request-init-data": urlencode(token_payload.get("payload"))}


def is_admin_user(token_payload):
    scope = token_payload.get("payload")["group_name"]
    return scope == "Supper Admin"


def is_default_user(token_payload):
    return token_payload["user_type"] in ["default", "admin"]
