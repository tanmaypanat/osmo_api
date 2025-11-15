import pytest
from aiohttp import web
from sqlalchemy import select, text

from app.db_models import Formula, FormulaMaterial, get_async_session
from app.event_queue import QUEUE_KEY, init_queue
from app.routes import setup_routes

integration_formula_payload = {
    "name": "Ocean Mist",
    "materials": [
        {"name": "Water", "concentration": 60.0},
        {"name": "Fragrance", "concentration": 40.0},
    ],
}


@pytest.mark.asyncio
async def test_formula_db_queue_and_duplicate(aiohttp_client):
    # create client inside test
    app = web.Application()
    setup_routes(app)
    init_queue(app)

    client = await aiohttp_client(app)

    # clear DB, ideally production code has a test DB isolated
    async with get_async_session() as session:
        async with session.begin():
            await session.execute(text("DELETE FROM formula_materials"))
            await session.execute(text("DELETE FROM formulas"))

    # first request
    resp = await client.post("/formulas", json=integration_formula_payload)
    assert resp.status == 201
    data = await resp.json()
    assert data["message"] == "New formula received and added"

    # check queue state
    queue = app[QUEUE_KEY]
    assert not queue.empty()
    queued_msg = queue._queue[
        0
    ]  # read, not consume, replace with get_nowait() if needed
    assert queued_msg["name"] == integration_formula_payload["name"]
    assert len(queued_msg["materials"]) == len(integration_formula_payload["materials"])

    # check DB state
    async with get_async_session() as session:
        # Formula row
        result = await session.execute(
            select(Formula).where(Formula.name == integration_formula_payload["name"])
        )
        formula = result.scalar_one_or_none()
        assert formula is not None

        # Materials
        result = await session.execute(
            select(FormulaMaterial).where(FormulaMaterial.formula_id == formula.id)
        )
        materials = result.scalars().all()
        assert len(materials) == len(integration_formula_payload["materials"])
        mat_names = {m.name for m in materials}
        payload_names = {m["name"] for m in integration_formula_payload["materials"]}
        assert mat_names == payload_names

    # send sae formula again to test duplicate handling
    resp2 = await client.post("/formulas", json=integration_formula_payload)
    assert resp2.status == 409
    data2 = await resp2.json()
    assert data2["message"] == "Formula already exists"
    assert queue.qsize() == 1  # still only one message in queue
