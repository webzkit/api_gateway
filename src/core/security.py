from typing import Optional
from config import settings
from core.authorization.authorize import Authorize


authorize = Authorize(expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


async def verify_token(token: Optional[str] = None):
    return await authorize.verify(token=token)


def generate_request_header(token_payload, token_bearer: Optional[str] = None):
    return (
        authorize.set_payload(token_payload)
        .set_token(token_bearer)
        .generate_request_init_data()
    )


def is_admin(token_payload):
    return authorize.set_payload(payload=token_payload).is_admin()
