from typing import Any
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.monitors.logger import Logger


auth_scheme = HTTPBearer()


logger = Logger(__name__)


def use_author_for_dev(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Any:

    return token.credentials
