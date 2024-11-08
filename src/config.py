from os import getenv
from typing import List, Union
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings

''' Project setting '''


class AppSetting(BaseSettings):
    APP_NAME: str = ""
    APP_API_PREFIX: str = ""
    APP_DOMAIN: str = ""
    APP_ENV: str = ""
    APP_PORT: str = ""

    BACKEND_CORS_ORIGINS: Union[List[AnyHttpUrl], str] = getenv(
        "BACKEND_CORS_ORIGINS", [])
    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


class CryptSetting(BaseSettings):
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 15
    TOKEN_VERIFY_EXPIRE: bool = False


class ServiceSetting(BaseSettings):
    USER_SERVICE_URL: str = ""
    AVATAR_SERVICE_URL: str = ""
    GATEWAY_TIMEOUT: int = 59


class Settings(AppSetting, CryptSetting, ServiceSetting):
    pass

settings = Settings()
