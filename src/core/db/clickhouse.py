from clickhouse_driver import Client


def clickhouse_client():
    client = Client(
        host="clickhouse", port=9000, user="default", password="your_password"
    )
    try:
        client.execute("SELECT 1")
        return client
    except Exception as e:
        print("error")
        raise


"""
async def db_clickhouse():
    client = get_clickhouse_client()
    try:
        yield client
    finally:
        client.disconnect()
"""
