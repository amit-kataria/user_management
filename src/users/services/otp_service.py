from users.utils.redis_client import redis_client
import secrets
from users.config.logging_config import get_logger

log = get_logger(__name__)


async def generate_otp(email: str) -> str:
    otp = str(secrets.randbelow(1000000)).zfill(6)
    # Store in Redis: key=otp:{email}, value=otp, ex=300 (5 mins)
    if redis_client.client:
        await redis_client.client.set(f"otp:{email}", otp, ex=300)
    else:
        log.warning("Redis not available, OTP not stored")
    return otp


async def verify_otp(email: str, otp: str) -> bool:
    if not redis_client.client:
        return False
    stored = await redis_client.client.get(f"otp:{email}")
    if stored and stored == otp:
        await redis_client.client.delete(f"otp:{email}")
        return True
    return False
