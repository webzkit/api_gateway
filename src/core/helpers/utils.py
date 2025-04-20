from typing import Dict, List, Optional, Union
from fastapi.encoders import jsonable_encoder
import hashlib


def parse_query_str(query_str: Union[str, None] = None) -> dict:
    if query_str is None:
        return {}

    return jsonable_encoder(query_str)


def get_nested_dic(dictionary: Dict, keys: Optional[List] = None):
    if not keys:
        # return None
        return dictionary

    return get_nested_dic(dictionary.get(keys[0], {}), keys[1:])


def sanitize_path(path: str) -> str:
    print(path)
    return path.strip("/").replace("/", "_")


def hashkey(key: str) -> str:
    return hashlib.md5(key.encode("utf-8")).hexdigest()
