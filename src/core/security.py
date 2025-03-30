from typing import Optional
from urllib.parse import urlencode
from core.monitors.logger import Logger
from config import settings
from core.authorization.jwt import JWTAuth
from core.authorization.authenticate import Authorization

logger = Logger(__name__)


jwt_auth = JWTAuth(expire_minute=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
authorize = Authorization()


async def verify_token(token: Optional[str] = None):
    return await jwt_auth.verify(token=token)


def generate_request_header(token_payload, token_bearer: Optional[str] = None):
    return (
        authorize.set_payload(token_payload)
        .set_token_bearer(token_bearer)
        .generate_request_init_data()
    )


def is_admin(token_payload):
    return authorize.set_payload(token_payload).is_admin()


## todo refactor
async def get_current_user_by(access_token: Optional[str] = None):
    if access_token is None:
        return None

    try:
        payload = await jwt_auth.decrypt(token=access_token)

        return payload["payload"]
    except Exception as error:
        logger.error(f"User not found by key {error}")

        return None
