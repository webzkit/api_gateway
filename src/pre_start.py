import asyncio
import logging
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from core.db.clickhouse import ClickHousePool
from config import settings
from core.consul.registry_service import register_service

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


async def create_database() -> None:
    ch_pool = ClickHousePool(database="default")
    with ch_pool as connection:
        try:
            connection.command(
                f"CREATE DATABASE IF NOT EXISTS {settings.LOGGER_DATABASE}"
            )
        except Exception as e:
            logger.debug(f"Failt to create database: {e}")
        finally:
            ch_pool.close()


async def create_table() -> None:
    ch_pool = ClickHousePool(database="default")
    with ch_pool as connection:
        try:
            connection.command(
                f"""
                CREATE TABLE IF NOT EXISTS {settings.LOGGER_DATABASE}.{settings.LOGGER_TABLE_LOG_REQUEST} (
                    asctime DateTime,
                    svname FixedString(50),
                    name FixedString(50),
                    uname FixedString(20),
                    levelname FixedString(10),
                    client_host FixedString(20),
                    method FixedString(20),
                    path FixedString(100),
                    request_body String,
                    message String,
                    status_code Int16) ENGINE = MergeTree
                ORDER BY asctime"""
            )
        except Exception as e:
            logger.debug(f"Failt to create table: {e}")
        finally:
            ch_pool.close()


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    await create_database()
    await create_table()


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def registry() -> None:
    await register_service()


async def main() -> None:
    logger.info("Initializing service")
    await init()
    await registry()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
