from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config("./.env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

BOOTSTRAP_SERVER=config("BOOTSTRAP_SERVER", cast=str)

KAFKA_ORDER_TOPIC=config("KAFKA_ORDER_TOPIC", cast=str)