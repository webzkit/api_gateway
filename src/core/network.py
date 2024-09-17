import aiohttp
import async_timeout
from config import settings


async def make_request(url: str, method: str, data: dict = {}, header: dict = {}):
    if not data:
        data = {}

    with async_timeout.timeout(settings.GATEWAY_TIMEOUT):
        async with aiohttp.ClientSession() as session:
            request = getattr(session, method)
            async with request(url, json=data, headers=header) as response:
                data = await response.json()
                return (data, response.status)
