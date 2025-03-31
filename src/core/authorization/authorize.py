from core.authorization.authenticate import Authorization
from core.authorization.jwt import JWTAuth
from core.authorization.define_key import PRIVATE_KEY, PUBLIC_KEY
from config import settings
from core.authorization.whitelist import WhiteList


class Authorize(JWTAuth, Authorization):
    def __init__(
        self,
        expire_minute: int = 10,
        algorithm: str = "RS256",
        public_key: str = PUBLIC_KEY,
        private_key: str = PRIVATE_KEY,
    ):
        JWTAuth.__init__(
            self,
            expire_minute=expire_minute,
            algorithm=algorithm,
            public_key=public_key,
            private_key=private_key,
        )

        self.wl_token = WhiteList()

    async def handle_logout(self):
        print(__name__)

    async def handle_login(self):
        access_token = self.encrypt(self.get_payload())
        refresh_token = self.set_exprire(settings.REFRESH_TOKEN_EXPIRE_MINUTES).encrypt(
            self.get_payload()
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def get_by(self, key: str):
        user = await self.user()
        if not user:
            return ""

        return user.get(key)

    async def user(self):
        payload = await self.decrypt(token=self.get_token_bearer())

        return self.set_payload(payload).get_payload()

    def get_payload_by(self, key: str, default: str = "") -> str:
        user = self.get_payload()
        if not user:
            return default

        return user.get(key, default)
