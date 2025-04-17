from core.authorization.constans import CACHE_KEY_WHITELIST_TOKEN
from core.authorization.store.token_manage import TokenManage


class WhiteList(TokenManage):
    def get_key_by(self, key: str, key_hash: str):
        return f"{CACHE_KEY_WHITELIST_TOKEN}:{key}:{self.hash(key_hash)}"
