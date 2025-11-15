import asyncio
import logging

_logger = logging.getLogger(__name__)

# name this queue in case we need multiple queues later
QUEUE_KEY = "publish_queue"


def init_queue(app):
    """
    Initialize the async queue and attach it to the app object.
    """
    app[QUEUE_KEY] = asyncio.Queue()


async def publish(app, payload):
    """
    Add a new payload to the queue.
    """
    queue: asyncio.Queue = app[QUEUE_KEY]
    await queue.put(payload)
    _logger.info(f"Payload queued: {payload}")


def rollback(app, payload):
    """
    Rollback a payload from the queue by removing it from the underlying deque.
    """
    queue: asyncio.Queue = app[QUEUE_KEY]
    try:
        # access private deque for simplicity, trade off with non async deque
        # faster than rebuilding the queue
        queue._queue.remove(payload)
        _logger.info(f"Payload rolled back: {payload}")
    except ValueError:
        _logger.warning(f"Payload not found in queue for rollback: {payload}")
