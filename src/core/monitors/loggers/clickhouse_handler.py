import logging

from clickhouse_driver import Client


class ClickHouseHandler(logging.Handler):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def emit(self, record):
        store = self._partial(record.__dict__)

        print(tuple(store.values()))

        """
        self.client.execute(
            "INSERT INTO log_requests (timestamp, svname, name, level, host, uname, message, status_code) VALUES",
            [tuple(store.values())],
        )
        """

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

        return {k: data[k] for k in to_keep}
