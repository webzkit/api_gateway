
from typing import Dict, List, Optional


def get_nested_dic(dictionary: Dict, keys: Optional[List] = None):
    if not keys:
        return dictionary

    return get_nested_dic(dictionary.get(keys[0], {}), keys[1:])
