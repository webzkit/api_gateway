import logging
from datetime import datetime
from collections import deque
import asyncio


class ClickHouseHandler(logging.Handler):
    def __init__(self, client_pool, buffer_size=100, flush_interval=5):
        super().__init__()
        self.client = client_pool

        self.buffer = deque(maxlen=buffer_size)
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval

        asyncio.create_task(self._periodic_flush())

    def emit(self, record):
        try:
            self.format(record)
            store = self._partial(record.__dict__)
            self.buffer.append(tuple(store.values()))
            if len(self.buffer) >= self.buffer_size:
                self._flush_buffer()
        except Exception as e:
            print(f"Failed to emit log to ClickHouse: {e}")

    def _flush_buffer(self):
        if self.buffer:
            try:
                log_records = list(self.buffer)
                self.writing_to_db(log_records)
            except Exception as e:
                print(f"Failed to flush logs to ClickHouse: {e}")

    # TODO Re-Check
    async def _periodic_flush(self):
        while True:
            await asyncio.sleep(self.flush_interval)
            if self.buffer:
                self._flush_buffer()

    def writing_to_db(self, log_records):
        with self.client as client:
            column_names = [
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

            try:
                client.insert("log_requests", log_records, column_names=column_names)
                self.buffer.clear()
            except Exception as e:
                print(e)
                pass
            finally:
                client.close()

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
