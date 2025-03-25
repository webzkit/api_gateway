import logging
from typing import Optional
import json


class StdoutFormatter(logging.Formatter):
    magenta = "\x1b[35;226m"
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
            logging.DEBUG: self.magenta + self.fmt + self.reset,
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
