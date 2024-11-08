from jwt import encode
import aiohttp
import async_timeout
from config import settings
from core.exceptions import ServiceHttpException


async def make_request(url: str, method: str, data: dict = {}, headers: dict = {}, params:dict = {}):
    if not data:
        data = {}

    with async_timeout.timeout(settings.GATEWAY_TIMEOUT):
        async with aiohttp.ClientSession() as session:
            request = getattr(session, method)
            async with request(url, json=data, headers=headers, params=params) as response:
                if response.ok:
                    data = await response.json()
                    return (data, response.status)

                res = await response.json()
                raise ServiceHttpException(res.get("detail"), response.status)
