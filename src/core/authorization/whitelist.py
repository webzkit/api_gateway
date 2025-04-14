import json

from fastapi.encoders import jsonable_encoder
from core.authorization.constans import CACHE_KEY_WHITELIST_TOKEN
from core.authorization.store.token_store import TokenStore


class WhiteList(TokenStore):
    def gen_key_by(self, key: str, key_hash: str):
        return f"{CACHE_KEY_WHITELIST_TOKEN}:{key}:{self.hash(key_hash)}"

    async def has_whitelist(self, key: str, key_hash: str) -> bool:
        return await self._cache.has(self.gen_key_by(key=key, key_hash=key_hash))

    async def revoke_all(self, key: str, value: str):
        token = self.replace_token_bearer(value)
        data = await self._cache.get(self.gen_key_by(key=key, key_hash=token))

        if data is None:
            return

        data = json.loads(jsonable_encoder(data))
        for k, v in data.items():
            if v == "bearer":
                continue

            await self._cache.delete(
                self.gen_key_by(
                    key=self.gen_key(key=k, uname=key.split(":")[-1]), key_hash=v
                )
            )
