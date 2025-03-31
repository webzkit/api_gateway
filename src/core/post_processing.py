from typing import Any, Dict
from core.security import authorize


async def processing_login_response(data: Dict) -> Any:
    return await authorize.set_payload(data.get("data", {})).handle_login()
