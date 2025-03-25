import logging
import json
from typing import Optional
from config import settings


class FileFormatter(logging.Formatter):
    LOGGING_FORMAT = "%(asctime)s - %(svname)s - %(name)s - %(levelname)s - %(host)s - %(uname)s - %(message)s - %(status_code)s"

    def __init__(self, fmt: Optional[str] = None):
        super().__init__()
        self.fmt = fmt or self.LOGGING_FORMAT

    def format(self, record):
        to_dict = json.loads(json.dumps(record.__dict__))

        record.host = to_dict.get("host", "unknow")
        record.uname = to_dict.get("uname", "unknow")
        record.status_code = to_dict.get("status_code", 0)
        record.svname = settings.SERVICE_NAME

        formatter = logging.Formatter(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)
