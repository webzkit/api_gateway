from abc import ABC, abstractmethod
from typing import Dict, Self


class JWTInterface(ABC):

    @abstractmethod
    async def encrypt(self, payload: Dict) -> str:
        pass

    @abstractmethod
    async def decrypt(self, token: str) -> Dict:
        pass

    @abstractmethod
    async def verify(self, token: str) -> Dict:
        pass
