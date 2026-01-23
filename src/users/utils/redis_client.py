import redis.asyncio as redis
from users.config.config import config
from users.config.logging_config import get_logger

log = get_logger(__name__)


class RedisClient:
    client: redis.Redis = None

    async def connect(self):
        try:
            log.info(f"Connecting to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
            self.client = redis.Redis(
                host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True
            )
            await self.client.ping()
            log.info("Connected to Redis")
        except Exception as e:
            log.error(f"Error connecting to Redis: {e}")
            raise e

    async def close(self):
        if self.client:
            await self.client.close()


redis_client = RedisClient()
