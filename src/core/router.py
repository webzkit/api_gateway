import json
import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from typing import Annotated, Any, List, Dict, Callable, Type
from pydantic import BaseModel, create_model


openapi_spec = {}
path = os.path.dirname(os.path.abspath(__file__))
jsonfile = f"{path}/openapi_engine.json"

try:
    with open(jsonfile, "r") as f:
        openapi_spec = json.load(f)
except FileNotFoundError:
    print("Error: File not found")
except json.JSONDecodeError as e:
    print(f"{e}")


# Hàm chuyển đổi schema OpenAPI sang Pydantic
def openapi_schema_to_pydantic(schema: Dict, schema_name: str) -> Type[BaseModel]:
    fields = {}
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get("type")
        nullable = prop_schema.get("nullable", False)

        # Ánh xạ kiểu dữ liệu OpenAPI sang Python
        if prop_type == "integer":
            field_type = int
        elif prop_type == "string":
            field_type = str
        elif prop_type == "number":
            field_type = float
        else:
            field_type = Any

        # Xử lý nullable
        if nullable:
            field_type = field_type | None

        # Đặt giá trị mặc định nếu không bắt buộc
        default = None if prop_name not in required else ...

        fields[prop_name] = Annotated[field_type, Field(default, **prop_schema)]

    # Tạo mô hình Pydantic động
    return create_model(schema_name, **fields)


# Tạo tất cả mô hình Pydantic từ components.schemas
pydantic_models = {}
schemas = openapi_spec.get("components", {}).get("schemas", {})
for schema_name, schema in schemas.items():
    pydantic_models[schema_name] = openapi_schema_to_pydantic(schema, schema_name)


# Hàm lấy Schema Pydantic từ $ref
def get_model_from_ref(ref: str) -> Type[BaseModel]:
    schema_name = ref.split("/")[-1]
    model = pydantic_models.get(schema_name, BaseModel)
    return model


# Hàm tạo cấu hình route từ openapi.json
def parse_openapi_to_route_config(openapi: Dict) -> List[Dict]:
    route_config = []
    paths = openapi.get("paths", {})

    for path, methods in paths.items():
        if path in [
            "/api/v1/users/{id}",
            "/api/v1/users/soft/{id}",
            "/",
            "/health",
            "/api/v1/authenticate/login",
            "/api/v1/authenticate/logout",
        ]:
            continue

        # TODO check remove
        prefix = path.strip("/")
        endpoints = []
        tags = set()

        for method, details in methods.items():
            tags.update(details.get("tags", []))

            # Lấy response_model
            response_schema = (
                details.get("responses", {})
                .get("200", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            response_model = None
            if response_schema.get("$ref", None) is None:
                print("todo check")
                # response_model = List[
                #    get_model_from_ref(response_schema["items"]["$ref"])
                # ]
            else:
                print("begin===========================================")
                print(path, method)
                ref = response_schema.get("$ref") or ""
                name = ref.split("/")[-1]
                print("=========================================end")
                response_model = get_model_from_ref(name)

            # Lấy request_body_model (cho POST)
            request_body = (
                details.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )

            request_body_model = (
                get_model_from_ref(request_body["$ref"])
                if "$ref" in request_body
                else None
            )

            # Lấy parameters
            parameters = details.get("parameters", [])

            endpoint = {
                "method": method,
                "path": path.replace(f"/{prefix}", "") or "/",
                "summary": details.get("summary", ""),
                "response_model": response_model,
                "request_body_model": request_body_model,
                "parameters": parameters,
            }

            endpoints.append(endpoint)

        route_config.append(
            {
                "prefix": prefix,
                "tag": tags.pop() if tags else prefix.capitalize(),
                "endpoints": endpoints,
            }
        )

    return route_config


# Hàm tạo handler động
def create_handlers(prefix: str) -> Dict[str, Callable]:
    items: List[BaseModel] = []

    async def get_items():
        return items

    async def create_item(item: BaseModel):
        items.append(item)
        return item

    return {"get_/": get_items, "post_/": create_item}


# Hàm đăng ký router động
def register_dynamic_router(config: Dict) -> APIRouter:
    prefix = config["prefix"]
    tag = config["tag"]
    router = APIRouter(prefix=f"/{prefix}", tags=[tag])
    handlers = create_handlers(prefix)

    for endpoint in config["endpoints"]:
        method = endpoint["method"].lower()
        path = endpoint["path"]
        handler_key = f"{method}_{path}"
        handler = handlers.get(handler_key)
        summary = endpoint["summary"]
        response_model = endpoint["response_model"]
        parameters = endpoint["parameters"]
        request_body_model = endpoint["request_body_model"]
        path = ""

        if handler:
            if method == "get":
                router.get(
                    path=path,
                    response_model=response_model,
                    summary=summary,
                    response_class=get_model_from_ref("UserRead")
                    openapi_extra={"parameters": parameters},
                )(handler)
            elif method == "post":
                # Sử dụng request_body_model cho tham số item
                async def wrapped_handler(
                    item: request_body_model = None,
                ):
                    return await handler(item)

                router.post(
                    path=path,
                    response_model=response_model,
                )(wrapped_handler)

    return router


def register_route(app: FastAPI):
    route_config = parse_openapi_to_route_config(openapi_spec)
    for config in route_config:
        router = register_dynamic_router(config)
        app.include_router(router)
