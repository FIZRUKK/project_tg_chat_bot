import os
from dotenv import load_dotenv



load_dotenv()

class RedisConfig:
    host = os.getenv("REDIS_HOSTNAME")
    port = int(os.getenv("REDIS_PORT"))

redis_config = RedisConfig()