from core.authorization.authenticate import Authorization
from core.authorization.jwt import JWTAuth
from core.authorization.define_key import PRIVATE_KEY, PUBLIC_KEY


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

    async def get_by(self, key: str):
        user = await self.user()
        if not user:
            return ""

        return user.get(key)

    async def user(self):
        payload = await self.decrypt(token=self.get_token_bearer())

        return self.set_payload(payload).get_payload()
