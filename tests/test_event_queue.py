import pytest
import asyncio
from app.event_queue import init_queue, publish, rollback, QUEUE_KEY


@pytest.mark.asyncio
async def test_publish_adds_payload():
    app = {}
    init_queue(app)

    payload = {"name": "Test Item", "value": 123}
    await publish(app, payload)

    queue: asyncio.Queue = app[QUEUE_KEY]
    # Accessing private deque to assert
    assert payload in queue._queue
    assert queue.qsize() == 1


@pytest.mark.asyncio
async def test_rollback_removes_payload():
    app = {}
    init_queue(app)

    payload1 = {"name": "Item1"}
    payload2 = {"name": "Item2"}

    # Add payloads
    await publish(app, payload1)
    await publish(app, payload2)

    queue: asyncio.Queue = app[QUEUE_KEY]
    assert queue.qsize() == 2

    # Rollback one payload
    rollback(app, payload1)
    assert payload1 not in queue._queue
    assert payload2 in queue._queue
    assert queue.qsize() == 1


@pytest.mark.asyncio
async def test_rollback_nonexistent_payload():
    app = {}
    init_queue(app)

    payload = {"name": "Nonexistent"}
    # Should not raise, only logs warning
    rollback(app, payload)

    queue: asyncio.Queue = app[QUEUE_KEY]
    assert queue.qsize() == 0  # still empty
