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


class RateLimitException(Exception):
    # TODO
    pass
