from typing import Optional, Dict
from urllib.parse import urlencode


class Authorization:
    SCOPE_SUPER_ADMIN = "Supper Admin"

    def __init__(self):
        self.__payload = {}
        self.__teoken_bearer = ""

    def set_payload(self, payload: Dict = {}):
        self.__payload = payload

        return self

    def get_payload(self):
        if "payload" in self.__payload:
            return self.__payload["payload"]

        return self.__payload

    def set_token_bearer(self, token_bearer: Optional[str] = ""):
        self.__teoken_bearer = token_bearer

        return self

    def get_token_bearer(self):
        return self.__teoken_bearer

    def generate_request_init_data(self):
        return {
            "request-init-data": urlencode(self.__payload),
            "Authorization": self.__teoken_bearer,
        }

    def is_admin(self):
        return self.SCOPE_SUPER_ADMIN == self.__get_scope()

    def __get_scope(self):
        return self.get_payload()["group"]["name"]
