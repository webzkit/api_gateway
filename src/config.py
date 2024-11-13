from enum import Enum
from os import getenv
from typing import List, Union
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings

""" Project setting """


class EnviromentOption(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AppSetting(BaseSettings):
    APP_NAME: str = ""
    APP_API_PREFIX: str = ""
    APP_DOMAIN: str = ""
    APP_ENV: Union[EnviromentOption, str] = getenv("APP_ENV", "development")
    APP_PORT: str = ""

    BACKEND_CORS_ORIGINS: Union[List[AnyHttpUrl], str] = getenv(
        "BACKEND_CORS_ORIGINS", []
    )

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


class RedisCacheSetting(BaseSettings):
    REDIS_CACHE_HOST: str = getenv("REDIS_CACHE_HOST", "redis")
    REDIS_CACHE_PORT: int = int(getenv("REDIS_CACHE_PORT", 6379))
    REDIS_CACHE_URL: str = f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}"


class RedisRateLimiterSetting(BaseSettings):
    REDIS_RATE_LIMIT_HOST: str = getenv("REDIS_RATE_LIMIT_HOST", "redis")
    REDIS_RATE_LIMIT_PORT: int = int(getenv("REDIS_RATE_LIMIT_PORT", 6379))
    REDIS_RATE_LIMIT_URL: str = (
        f"redis://{REDIS_RATE_LIMIT_HOST}:{REDIS_RATE_LIMIT_PORT}"
    )

    REDIS_RATE_LIMIT_LIMIT: int = int(getenv("DEFAULT_RATE_LIMIT_LIMIT", 100))
    REDIS_RATE_LIMIT_PERIOD: int = int(getenv("DEFAULT_RATE_LIMIT_PERIOD", 3600))


class ServiceSetting(BaseSettings):
    USER_SERVICE_URL: str = ""
    AVATAR_SERVICE_URL: str = ""
    GATEWAY_TIMEOUT: int = 59


class Settings(
    AppSetting,
    CryptSetting,
    RedisCacheSetting,
    RedisRateLimiterSetting,
    ServiceSetting,
):
    pass


settings = Settings()
