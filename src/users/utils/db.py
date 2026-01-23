from motor.motor_asyncio import AsyncIOMotorClient
from users.config.config import config
from users.config.logging_config import get_logger

log = get_logger(__name__)


class Database:
    client: AsyncIOMotorClient = None

    def connect(self):
        try:
            log.info(f"Connecting to MongoDB at {config.MONGO_URI}")
            self.client = AsyncIOMotorClient(config.MONGO_URI)
            # Verify connection
            # await self.client.admin.command('ping') # Can't await in sync init, do in startup
            log.info("MongoDB client created")
        except Exception as e:
            log.error(f"Error connecting to MongoDB: {e}")
            raise e

    def get_db(self):
        return self.client[config.MONGO_DB_NAME]

    def close(self):
        if self.client:
            self.client.close()


db = Database()
