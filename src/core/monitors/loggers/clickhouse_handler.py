import logging
from datetime import datetime
from clickhouse_driver import Client


"""
CREATE TABLE default.log_requests (
  `timestamp` DateTime,
  `svname` String,
  `name` String,
  `level` String,
  `host` String,
  `uname` String,
  `message` String,
  `status_code` String
) ENGINE = MergeTree
ORDER BY
  timestamp
"""


class ClickHouseHandler(logging.Handler):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def emit(self, record):
        store = self._partial(record.__dict__)

        self.client.execute(
            "INSERT INTO log_requests (asctime, svname, name, level, host, uname, message, status_code) VALUES",
            [tuple(store.values())],
        )

    def _partial(self, data):
        to_keep = [
            "asctime",
            "svname",
            "name",
            "levelname",
            "host",
            "uname",
            "message",
            "status_code",
        ]
        partial = {}
        for column in to_keep:
            if column == "asctime":
                partial[column] = datetime.strptime(data[column], "%Y-%m-%d %H:%M:%S")
                continue

            partial[column] = data[column]

        return partial
