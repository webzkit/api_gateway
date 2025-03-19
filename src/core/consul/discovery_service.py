import consul
from config import settings
import requests
from fastapi import HTTPException
from core.logger import logging

logger = logging.getLogger(__name__)


async def discover_service(service_name: str) -> str:
    consul_url = f"http://{settings.CONSUL_HOST}:{settings.CONSUL_PORT}/v1/catalog/service/{service_name}"
    try:
        response = requests.get(consul_url)
        print(response.json())
        if response.status_code == 200 and response.json():
            service = response.json()[0]

            return f"http://{service['ServiceAddress']}:{service['ServicePort']}"
        else:
            raise HTTPException(
                status_code=503, detail=f"Service {service_name} not found in Consul"
            )
    except Exception as e:
        logger.error(f"Error discovering service {service_name}: {e}")

        raise HTTPException(status_code=503, detail="Service discovery failed")
