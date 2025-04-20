from pydantic import BaseModel


class BlackListTokenSchema(BaseModel):
    refresh_token: str

    def to_dict(self):
        return self.model_dump()


class WhiteListTokenSchema(BaseModel):
    access_token: str
    refresh_token: str

    def to_dict(self):
        return self.model_dump()
