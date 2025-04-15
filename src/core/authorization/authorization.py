from typing import Optional, Dict
from urllib.parse import urlencode
from core.authorization.jwt import JWTAuth


class Authorization(JWTAuth):
    SCOPE_SUPER_ADMIN = ["Supper Admin"]

    def __init__(self, expire_minute: int = 10, algorithm: str = "RS256"):
        self._payload = {}
        self._token = ""

        JWTAuth.__init__(self, expire_minute=expire_minute, algorithm=algorithm)

    def set_payload(self, payload: Dict = {}):
        self._payload = payload

        return self

    def get_payload(self):
        if "payload" in self._payload:
            return self._payload["payload"]

        return self._payload

    def set_token(self, token: Optional[str] = None):
        self._token = token

        return self

    def get_token(self):
        return self._token

    def generate_request_init_data(self):
        return {
            "request-init-data": urlencode(self._payload),
            "Authorization": self.get_token(),
        }

    def is_admin(self):
        return self.__get_scope() in self.SCOPE_SUPER_ADMIN

    async def get_by(self, key: str):
        user = await self.user()
        if not user:
            return ""

        return user.get(key)

    async def user(self):
        payload = await self.decrypt(token=self.get_token())

        return self.set_payload(payload).get_payload()

    def get_payload_by(self, key: str, default: str = "") -> str:
        user = self.get_payload()
        if not user:
            return default

        return user.get(key, default)

    def __get_scope(self):
        return self.get_payload()["group"]["name"]
