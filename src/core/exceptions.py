from typing import Union
from fastapi import HTTPException, status
from http import HTTPStatus


class AuthTokenMissing(Exception):
    pass


class AuthTokenExpired(Exception):
    pass


class AuthTokenCorrupted(Exception):
    pass


class ServiceHttpException(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

        def __str__(self):
            return f"{self.message} (Error Code: {self.error_code})"


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Union[str, None] = None,
    ):
        if not detail:  # pragma: no cover
            detail = HTTPStatus(status_code).description
        super().__init__(status_code=status_code, detail=detail)


class RateLimitException(CustomException):
    def __init__(self, detail: Union[str, None] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail
        )  # pragma: no cover


