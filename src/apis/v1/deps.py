from typing import Any
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


auth_scheme = HTTPBearer()


def is_supper_admin(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> Any:
    return token.credentials
