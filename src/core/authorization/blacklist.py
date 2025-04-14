from typing import Self


class BlackList:
    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token

    def create(self):
        pass

    def notify(self):
        pass

    def get(self) -> str:
        return self.refresh_token

    def set(self, refresh_token: str) -> Self:
        self.refresh_token = refresh_token

        return self
