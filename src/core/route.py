import aiohttp
import functools
from typing import Any, Dict, List, Optional
from importlib import import_module
from fastapi import Request, Response, HTTPException, status

from .exception.auth_exception import (
    AuthTokenMissing,
    AuthTokenExpired,
    AuthTokenCorrupted,
)

from core.exception.http_exception import ServiceHttpException
from fastapi.encoders import jsonable_encoder
from .client import make_request
from core.helpers.utils import parse_query_str
from core.consul.discovery_service import discover_service
from core.caching.use_cache import use_cache


def route(
    request_method,
    path: str,
    status_code: int,
    payload_key: Optional[str],
    service_name: str,
    authentication_required: bool = False,
    post_processing_func: Optional[str] = None,
    authentication_token_decoder: str = "core.security.verify_token",
    service_authorization_checker: Optional[str] = "core.security.is_admin",
    service_header_generator: Optional[str] = "core.security.generate_request_header",
    response_model: Optional[str] = None,
    response_list: bool = False,
    cache_key_prefix: Optional[str] = None,
    cache_resource_id_name: Any = None,
    cache_resource_id_type: type | tuple[type, ...] = int,
):
    if response_model:
        response_model = import_function(response_model)  # type: ignore
        if response_list:
            response_model = List[response_model]  # type: ignore

    app_any = request_method(
        path, status_code=status_code, response_model=response_model
    )

    def wrapper(f):
        @app_any
        @functools.wraps(f)
        async def inner(request: Request, response: Response, **kwargs):
            service_headers = {}
            token_payload = {}

            # Check authentication
            if authentication_required:
                try:
                    token_bearer = request.headers.get("authorization", "")
                    token_payload = await authenticate(
                        token_bearer, authentication_token_decoder
                    )

                    # check permission
                    await check_user_eligible(
                        token_payload, service_authorization_checker
                    )

                    # Generate headers
                    if service_header_generator:
                        header_generator = import_function(service_header_generator)
                        service_headers = header_generator(token_payload, token_bearer)

                except Exception as error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=str(error),
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            scope = request.scope
            method = scope["method"].lower()
            path = scope["path"]
            request_param = parse_query_str(str(request.query_params))

            payload_obj = kwargs.get(str(payload_key))
            payload = jsonable_encoder(payload_obj) if payload_obj else {}
            discover_url = await discover_service(service_name)
            url = f"{discover_url}{path}"

            resp_data, status_code_from_service = await call_to_service(
                request,
                url=url,
                method=method,
                payload=payload,
                service_headers=service_headers,
                request_param=request_param,
                cache_key_prefix=cache_key_prefix,
                cache_resource_id_name=cache_resource_id_name,
                cache_resource_id_type=cache_resource_id_type,
                cache_kwargs=kwargs,
            )

            response.status_code = status_code_from_service

            # status code is None from to cache
            if status_code_from_service is None:
                response.status_code = status_code

            if all([status_code_from_service == status_code, post_processing_func]):
                post_processing_f = import_function(post_processing_func)
                resp_data = await post_processing_f(resp_data)  # type: ignore

            return resp_data

    return wrapper


async def check_user_eligible(
    token_payload: dict, func_use: Optional[str] = None
) -> None:
    if func_use is None:
        return

    authorization_checker = import_function(func_use)
    is_user_eligible = authorization_checker(token_payload)

    if is_user_eligible:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are allowed to access this scope",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate(token_bearer: str, func_use: str) -> Any:
    token_decoder = import_function(func_use)
    exc = None

    try:
        return await token_decoder(token_bearer)  # type: ignore
    except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted) as e:
        exc = str(e)
    except Exception as e:
        exc = str(e)
    finally:
        if exc:
            raise Exception(f"{exc}")


@use_cache()
async def call_to_service(
    request: Request,
    url: str,
    method: str,
    payload: Dict = {},
    service_headers: Any = {},
    request_param: Dict = {},
    cache_key_prefix: Optional[str] = None,
    cache_resource_id_name: Any = None,
    cache_resource_id_type: type | tuple[type, ...] = int,
    cache_kwargs: Any = None,
):
    try:
        resp_data, status_code_from_service = await make_request(
            url=url,
            method=method,
            data=payload,
            headers=service_headers,  # type: ignore
            params=request_param,
        )
    except aiohttp.ClientConnectorError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except aiohttp.ContentTypeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service error.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ServiceHttpException as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return resp_data, status_code_from_service


def import_function(method_path):
    module, method = method_path.rsplit(".", 1)
    module_import = import_module(module)

    return getattr(module_import, method, lambda *args, **kwargs: None)  # type: ignore
