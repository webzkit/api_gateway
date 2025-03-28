from enum import Enum
from os import getenv
from typing import List, Union
from pydantic import Field, field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

""" Project setting """


class EnviromentOption(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AppSetting(BaseSettings):
    APP_NAME: str = Field(default="App name")
    APP_API_PREFIX: str = Field(default="/api/v1")
    APP_ENV: Union[EnviromentOption, str] = getenv("APP_ENV", "development")

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
    #  60 minutes * 24 hours * 1 days = 1440
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 2880)
    )
    TOKEN_VERIFY_EXPIRE: bool = bool(getenv("TOKEN_VERIFY_EXPIRE", False))


class RedisCacheSetting(BaseSettings):
    REDIS_CACHE_HOST: str = getenv("REDIS_HOST", "redis")
    REDIS_CACHE_PORT: int = int(getenv("REDIS_PORT", 6379))
    REDIS_CACHE_DB: int = int(getenv("REDIS_CACHE_DB", 0))
    REDIS_CACHE_PASSWORD: str = getenv("REDIS_PASSWORD", "secret")

    # <subprotocol>://<username>:<password>@<host>:<port>/<db>
    REDIS_CACHE_URL: str = (
        f"redis://:{REDIS_CACHE_PASSWORD}@{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}/{REDIS_CACHE_DB}"
    )


class RedisRateLimiterSetting(BaseSettings):
    REDIS_RATE_LIMIT_HOST: str = getenv("REDIS_HOST", "redis")
    REDIS_RATE_LIMIT_PORT: int = int(getenv("REDIS_PORT", 6379))
    REDIS_RATE_DB: int = int(getenv("REDIS_RATE_DB", 0))
    REDIS_RATE_PASSWORD: str = getenv("REDIS_PASSWORD", "secret")

    REDIS_RATE_LIMIT_URL: str = (
        f"redis://:{REDIS_RATE_PASSWORD}@{REDIS_RATE_LIMIT_HOST}:{REDIS_RATE_LIMIT_PORT}/{REDIS_RATE_DB}"
    )
    REDIS_RATE_LIMIT_LIMIT: int = int(getenv("DEFAULT_RATE_LIMIT_LIMIT", 100))
    REDIS_RATE_LIMIT_PERIOD: int = int(getenv("DEFAULT_RATE_LIMIT_PERIOD", 3600))


class ClickhouseSetting(BaseSettings):
    CLICKHOUSE_HOST: str = Field(default="clickhouse")
    CLICKHOUSE_POST: int = Field(default=8123)
    CLICKHOUSE_USERNAME: str = Field(default="default")
    CLICKHOUSE_PASSWORD: str = Field(default="your_password")
    CLICKHOUSE_POOL_SIZE: int = Field(default=5)


class LoggerSetting(BaseSettings):
    LOGGER_DATABASE: str = Field(default="loggers")
    LOGGER_TABLE_LOG_REQUEST: str = Field(default="log_requests")
    LOGGER_BUFFER_SIZE: int = Field(default=100)  # 100 Records
    LOGGER_FLUSH_INTERVAL: int = Field(default=30)  # 30Seconds


class ServiceSetting(BaseSettings):
    GATEWAY_TIMEOUT: int = int(getenv("HTTP_TIMEOUT_SERVICE", 60))

    CONSUL_HOST: str = getenv("CONSUL_HOST", "consul")
    CONSUL_PORT: int = int(getenv("CONSUL_PORT", 8500))
    CONSUL_INTERVAL: str = getenv("CONSUL_INTERVAL", "10s")
    CONSUL_TIMEOUT: str = getenv("CONSUL_TIMEOUT", "5s")

    SERVICE_NAME: str = getenv("APIGATEWAY_SERVICE_NAME", "api_gateway")
    SERVICE_PORT: int = int(getenv("APIGATEWAY_SERVICE_PORT", 8000))
    ENGINE_SERVICE_NAME: str = getenv("ENGINE_SERVICE_NAME", "engine")
    AVATAR_SERVICE_NAME: str = getenv("AVATAR_SERVICE_NAME", "avatar")


class Settings(
    AppSetting,
    CryptSetting,
    RedisCacheSetting,
    RedisRateLimiterSetting,
    ServiceSetting,
    ClickhouseSetting,
    LoggerSetting,
):
    model_config = SettingsConfigDict(env_prefix="APIGATEWAY__")
    pass


settings = Settings()
