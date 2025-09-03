import logging
import os
from logging.handlers import RotatingFileHandler
from config import settings
from .loggers.stdout_formatter import StdoutFormatter
from .loggers.file_formatter import FileFormatter
from .loggers.clickhouse_handler import ClickHouseHandler
from core.db.clickhouse import ClickHousePool

ch_pool = ClickHousePool()


class Logger:
    MAX_SIZE_STORE_LOGFILE = 10485760  # 10M
    MAX_FILE_STORE_LOGFILE = 5

    def __init__(
        self,
        name: str = __name__,
        level: int = logging.DEBUG,
        filename: str = "app.log",
    ):
        self.filename = filename
        self.logger = logging.getLogger(name)
        self.logger.propagate = True
        self.logger.setLevel(level)
        self.logger.handlers = [
            # self._store_to_file(),
            self._store_to_db(),
            # self._stdout(),
        ]

    def _stdout(self):
        handler = logging.StreamHandler()
        handler.setFormatter(StdoutFormatter())

        return handler

    def _store_to_db(self):
        handler = ClickHouseHandler(
            client_pool=ch_pool,
            buffer_size=settings.LOGGER_BUFFER_SIZE,
            flush_interval=settings.LOGGER_FLUSH_INTERVAL,
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(FileFormatter())

        return handler

    def _store_to_file(self):
        handler = RotatingFileHandler(
            self._get_log_file_path(),
            maxBytes=self.MAX_SIZE_STORE_LOGFILE,
            backupCount=self.MAX_FILE_STORE_LOGFILE,
        )
        handler.setLevel(logging.WARNING)
        handler.setFormatter(FileFormatter())

        return handler

    def _get_log_file_path(self):
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
        )

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return os.path.join(log_dir, f"{self.filename}")

    def __getattr__(self, name):
        if hasattr(self.logger, name):
            return lambda message, **kwargs: getattr(self.logger, name)(
                message, extra=kwargs.get("extra", {})
            )

        raise AttributeError(f"'{self.__class__.__name__}' has not function '{name}'")
