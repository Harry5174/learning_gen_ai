import os
from starlette.config import Config
from starlette.datastructures import Secret

# Print current working directory
print("Current working directory:", os.getcwd())

# Absolute path to the .env file
env_file_path = os.path.join(os.getcwd(), ".env")
print("Using .env file at:", env_file_path)

config = Config(env_file_path)

DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

print("DATABASE_URL:", DATABASE_URL)
print("BOOTSTRAP_SERVER:", BOOTSTRAP_SERVER)
print("KAFKA_ORDER_TOPIC:", KAFKA_ORDER_TOPIC)
print("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT:", KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT)
print("TEST_DATABASE_URL:", TEST_DATABASE_URL)
