import logging
import json
from logging.handlers import RotatingFileHandler
from typing import Optional
from config import settings
import os


class FileFormatter(logging.Formatter):
    LOGGING_FORMAT = "%(asctime)s - %(svname)s - %(name)s - %(levelname)s - %(client_host)s - %(uname)s - %(message)s - %(status_code)s"

    def __init__(
        self,
        fmt: Optional[str] = None,
        filename: str = "app.log",
        max_size_store_logfile=10485760,  # default 10 Megabyte
        max_file_store_logfile=5,
    ):
        super().__init__()
        self.fmt = fmt or self.LOGGING_FORMAT
        self.filename = filename
        self.max_size_store_logfile = max_size_store_logfile
        self.max_file_store_logfile = max_file_store_logfile

    def handler(self):
        handler = RotatingFileHandler(
            self._get_log_file_path(),
            maxBytes=self.max_size_store_logfile,
            backupCount=self.max_file_store_logfile,
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(self)

        return handler

    def format(self, record):
        to_dict = json.loads(json.dumps(record.__dict__))

        record.client_host = to_dict.get("client_host", "unknow")
        record.uname = to_dict.get("uname", "unknow")
        record.status_code = to_dict.get("status_code", 0)
        record.svname = settings.SERVICE_NAME
        record.request_body = to_dict.get("request_body", "")

        formatter = logging.Formatter(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)

    def _get_log_file_path(self):
        # ./src/logs
        log_dir = os.path.join(
            os.path.dirname(os.path.abspath(os.curdir)),
            "zkit/logs",
        )

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return os.path.join(log_dir, f"{self.filename}")
