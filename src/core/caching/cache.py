from typing import Optional, Self, Any

from fastapi import Request
from core.exception.cache_exception import CacheIdentificationInferenceError
import re


class Caching:
    def __init__(self, key_prefix: Optional[str] = None) -> None:
        self.key_prefix = None

    async def get_or_set(self, request: Request, *args, **kwargs) -> None:
        self.key_prefix = kwargs.get("cache_key_prefix", None)

        if self.key_prefix is None:
            return

        print(kwargs.get("cache_resource_id_name"))
        return

    def set_key_prefix(self, key_prefix: str) -> Self:
        self.key_prefix = key_prefix

        return self

    def get_key_prefix(self) -> str:

        return self.key_prefix or ""

    def _infer_resource_id(
        self, kwargs: dict[str, Any], resource_id_type: type | tuple[type, ...]
    ) -> int | str:
        resource_id: int | str | None = None

        for arg_name, arg_value in kwargs.items():
            if isinstance(arg_value, resource_id_type):
                if (resource_id_type is int) and ("id" in arg_name):
                    resource_id = arg_value

                elif (resource_id_type is int) and ("id" not in arg_name):
                    pass

                elif resource_id_type is str:
                    resource_id = arg_value

        if resource_id is None:
            raise CacheIdentificationInferenceError

        return resource_id

    def __extract_data_inside_brackets(self, input_string: str) -> list[str]:
        data_inside_brackets = re.findall(r"{(.*?)}", input_string)

        return data_inside_brackets

    def __construct_data_dict(
        self, data_inside_brackets: list[str], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        data_dict = {}
        for key in data_inside_brackets:
            data_dict[key] = kwargs[key]

        return data_dict

    def _format_prefix(self, prefix: str, kwargs: dict[str, Any]) -> str:
        data_inside_brackets = self.__extract_data_inside_brackets(prefix)
        data_dict = self.__construct_data_dict(data_inside_brackets, kwargs)
        formatted_prefix = prefix.format(**data_dict)

        return formatted_prefix
