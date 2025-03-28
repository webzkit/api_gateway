import threading
from queue import Queue, Empty
import clickhouse_connect
from config import settings


class ClickHousePool:
    def __init__(
        self,
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_POST,
        username=settings.CLICKHOUSE_USERNAME,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.LOGGER_DATABASE,
        pool_size=settings.CLICKHOUSE_POOL_SIZE,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()

        self._initialize_pool()

    def _create_connection(self):
        return clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )

    def _initialize_pool(self):
        for _ in range(self.pool_size):
            client = self._create_connection()
            self.pool.put(client)

    def get_connection(self, timeout=5):
        try:
            client = self.pool.get(timeout=timeout)
            return client
        except Empty:
            raise Exception("No available connections in the pool")

    def release_connection(self, client):
        if client:
            self.pool.put(client)

    def close(self):
        with self.lock:
            while not self.pool.empty():
                client = self.pool.get()
                client.close()

    def __enter__(self):
        self.client = self.get_connection()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_connection(self.client)
