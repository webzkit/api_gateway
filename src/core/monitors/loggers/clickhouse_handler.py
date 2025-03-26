import logging
from datetime import datetime
from clickhouse_driver import Client


"""
CREATE TABLE default.log_requests (
  `asctime` DateTime,
  `svname` FixedString(50),
  `name` FixedString(50),
  `uname` FixedString(20),
  `levelname` FixedString(10),
  `client_host` FixedString(20),
  `method` FixedString(20),
  `path` FixedString(100),
  `request_body` String,
  `message` String,
  `status_code` Int16
) ENGINE = MergeTree
ORDER BY asctime
"""


class ClickHouseHandler(logging.Handler):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def emit(self, record):
        try:
            self.format(record)
            store = self._partial(record.__dict__)

            self.client.execute(
                "INSERT INTO log_requests (asctime, svname, name, uname, levelname, client_host, method, path,request_body, message, status_code) VALUES",
                [tuple(store.values())],
            )
        except Exception:
            self.handleError(record)

    def _partial(self, data):
        to_keep = [
            "asctime",
            "svname",
            "name",
            "uname",
            "levelname",
            "client_host",
            "method",
            "path",
            "request_body",
            "message",
            "status_code",
        ]
        partial = {}
        for column in to_keep:
            if column == "asctime":
                partial[column] = datetime.strptime(data[column], "%Y-%m-%d %H:%M:%S")
                continue

            partial[column] = data.get(column, "")

        return partial
