from datetime import datetime
from typing import Union

from sqlalchemy import Column


def get_int_from_datetime(value: Union[datetime, Column]) -> int:
    if not isinstance(value, datetime):
        raise TypeError('a datetime is required')

    return int(value.timestamp())
