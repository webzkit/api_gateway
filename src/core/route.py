import aiohttp
import functools
from typing import Any, Dict, List, Optional
from importlib import import_module
from fastapi import Request, Response, HTTPException, status

from core.helpers.cache import use_cache

from .exceptions import (
    AuthTokenMissing,
    AuthTokenExpired,
    AuthTokenCorrupted,
    ServiceHttpException,
)
from fastapi.encoders import jsonable_encoder
from .client import make_request
from core.helpers.utils import parse_query_str


def route(
    request_method,
    path: str,
    status_code: int,
    payload_key: Optional[str],
    service_url: str,
    authentication_required: bool = False,
    post_processing_func: Optional[str] = None,
    authentication_token_decoder: str = "core.security.decode_access_token",
    service_authorization_checker: Optional[str] = "core.security.is_admin_user",
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

    # TODO refactor func
    def wrapper(f):
        @app_any
        @functools.wraps(f)
        async def inner(request: Request, response: Response, **kwargs):
            service_headers = {}
            token_payload = {}

            # Check authentication
            if authentication_required:
                # Authentication
                authorization = request.headers.get("authorization")
                token_decoder = import_function(authentication_token_decoder)
                exc = None

                try:
                    token_payload = await token_decoder(authorization)  # type: ignore
                except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted) as e:
                    exc = str(e)
                except Exception as e:
                    exc = str(e)
                finally:
                    if exc:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=exc,
                            headers={"WWW-Authenticate": "Bearer"},
                        )

                # Authorization
                if service_authorization_checker:
                    authorization_checker = import_function(
                        service_authorization_checker
                    )

                    is_user_eligible = authorization_checker(token_payload)

                    if not is_user_eligible:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are allowed to access this scope",
                            headers={"WWW-Authenticate": "Bearer"},
                        )

                # Service headers
                if service_header_generator:
                    header_generator = import_function(service_header_generator)
                    service_headers = header_generator(token_payload, authorization)

            scope = request.scope
            method = scope["method"].lower()
            path = scope["path"]
            request_param = parse_query_str(str(request.query_params))

            payload_obj = kwargs.get(str(payload_key))
            payload = jsonable_encoder(payload_obj) if payload_obj else {}
            url = f"{service_url}{path}"

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
