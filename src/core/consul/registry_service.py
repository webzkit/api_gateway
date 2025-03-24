from time import sleep
from config import settings
import consul
from core.logger import Logger

logger = Logger(__name__)


async def register_service():
    check_http = consul.Check.http(
        f"http://{settings.SERVICE_NAME}:{settings.SERVICE_PORT}/health",
        interval=f"{settings.CONSUL_INTERVAL}",
        timeout=f"{settings.CONSUL_TIMEOUT}",
    )
    client = consul.Consul(host=settings.CONSUL_HOST, port=settings.CONSUL_PORT)

    while True:
        try:
            client.agent.service.register(
                name=settings.SERVICE_NAME,
                address=settings.SERVICE_NAME,
                port=settings.SERVICE_PORT,
                check=check_http,
                tags=["api", "api_gateway"],
            )
            break
        except consul.ConsulException:
            logger.error("Retrying to connect to consul ...")

            sleep(0.5)
