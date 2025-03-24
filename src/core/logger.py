import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    MAX_SIZE_STORE_LOGFILE = 10485760  # 10M
    MAX_FILE_STORE_LOGFILE = 5

    def __init__(self, name: str = __name__, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.logger.handlers = [self._stdout(), self._store_to_file()]

    def _stdout(self):
        handler = logging.StreamHandler()
        handler.setFormatter(StdoutFormatter())

        return handler

    def _store_to_file(self):
        handler = RotatingFileHandler(
            self._get_log_file_path(),
            maxBytes=self.MAX_SIZE_STORE_LOGFILE,
            backupCount=self.MAX_FILE_STORE_LOGFILE,
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(FileStorageFormatter(fmt=None))

        return handler

    def _get_log_file_path(self):
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return os.path.join(log_dir, "app.log")

    def _store_to_db(self):
        pass

    def __getattr__(self, name):
        if hasattr(self.logger, name):
            """
            return lambda message, **kwargs: getattr(self.logger, name)(
                message, extra=kwargs.get("extra", {})
            )
            """

            log_method = getattr(self.logger, name)

            def log_wrapper(message, **kwargs):
                extra = kwargs.get("extra", {})
                return log_method(message, extra=extra)

            return log_wrapper

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


class StdoutFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    LOGGING_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    def __init__(self, fmt: Optional[str] = None):
        super().__init__()
        self.fmt = fmt or self.LOGGING_FORMAT

        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        to_dict = json.loads(json.dumps(record.__dict__))
        record.host = to_dict.get("host", "unknow")
        record.uname = to_dict.get("uname", "unknow")

        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)


class FileStorageFormatter(logging.Formatter):
    LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(host)s - %(uname)s - %(message)s - %(status_code)s"

    def __init__(self, fmt: Optional[str] = None):
        super().__init__()
        self.fmt = fmt or self.LOGGING_FORMAT

    def format(self, record):
        to_dict = json.loads(json.dumps(record.__dict__))
        record.host = to_dict.get("host", "host unknow")
        record.uname = to_dict.get("uname", "uname unknow")
        record.status_code = to_dict.get("status_code", "status_code unknow")

        formatter = logging.Formatter(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)
