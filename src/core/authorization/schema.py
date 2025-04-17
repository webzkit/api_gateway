from pydantic import BaseModel


class TOKEN_BACKEND(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    def to_dict(self):
        return self.model_dump()
