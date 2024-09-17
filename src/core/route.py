import aiohttp
from typing import List, Optional, Union
importlib import import_module


def route(
    request_method,
    path: str,
    status_code: int,
    payload_key: str,
    service_url: str,
    authentication_required: bool = False,
    post_processing_func: Optional[str] = None,
    authentication_token_decoder: str = 'auth.decode_access_token',
    service_authorization_checker: str = 'auth.is_admin_user',
    service_header_generator: str = 'auth.generate_request_header',
    response_model: str | None = None,
    response_list: bool = False
):
    get_response_model = response_model
    if response_model:
        get_response_model = import_function(response_model)
        if response_list:
            get_response_model = List[get_response_model]

    app_any = request_method(
        path,
        status_code=status_code,
        response_model=get_response_model
    )


def import_function(method_path: str | None):
    if not method_path:
        return

    module, method = method_path.rsplit('.', 1)
    module_import = import_module(module)

    return getattr(module_import, method, lambda *args, **kwargs: None)
