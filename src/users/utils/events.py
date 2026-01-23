from users.utils.redis_client import redis_client
import json
from users.config.logging_config import get_logger

log = get_logger(__name__)


async def publish_event(stream_key: str, event_type: str, data: dict):
    """
    Publish an event to a Redis Stream.
    :param stream_key: The key of the stream (e.g. 'user_events')
    :param event_type: Event type (e.g. 'USER_CREATED')
    :param data: Dictionary data payload
    """
    try:
        if redis_client.client:
            payload = {"type": event_type, "data": json.dumps(data, default=str)}
            await redis_client.client.xadd(stream_key, payload)
            log.info(f"Published event {event_type} to {stream_key}")
        else:
            log.warning("Redis client not scheduled, event skipped")
    except Exception as e:
        log.error(f"Failed to publish event: {e}")
