import asyncio
import hashlib
import logging
import re

import aiohttp.web as web
from pydantic import ValidationError

from app.db_models import add_formula, check_formula_exists, get_all_formulas
from app.event_queue import publish, rollback
from app.schemas import Formulation, Material

_logger = logging.getLogger(__name__)

retries = 2  # total attempts = retries + 1


def create_hash(materials: list[Material]) -> str:
    normalized = []

    for m in materials:
        name = m.name.strip().lower()
        name = re.sub(r"\s+", "", name)
        conc = round(float(m.concentration), 3)

        normalized.append((name, conc))

    normalized.sort(key=lambda x: x[0])

    canonical = ";".join(f"{name}:{conc:.3f}" for name, conc in normalized)
    _logger.info(f"Canonical materials string: {canonical}")

    return hashlib.sha256(canonical.encode()).hexdigest()


async def publish_and_save(app, formula, materials_hash):
    attempt = 0

    while attempt <= retries:
        try:
            payload = {
                "name": formula.name,
                "materials": [
                    {"name": m.name, "concentration": m.concentration}
                    for m in formula.materials
                ],
                "materials_hash": materials_hash,
            }

            # publish to queue first
            await publish(app, payload)

            # then save to DB
            await add_formula(formula, materials_hash)

            return True

        except Exception as e:
            _logger.exception(f"Attempt {attempt + 1} failed: {e}")
            rollback(app, payload)
            attempt += 1
            await asyncio.sleep(0.1)  # short delay before retry

    # failed all attempts
    return False


async def handle_create_formula(request):
    data = await request.json()
    try:
        formula = Formulation(**data)
    except ValidationError as e:
        return web.json_response(
            {
                "error": f"Invalid Data: {e}",
            },
            status=400,
        )

    materials_hash = create_hash(formula.materials)

    existing_formula = await check_formula_exists(materials_hash)
    if existing_formula:
        _logger.info(f"Duplicate formula detected with ID: {existing_formula.id}")
        return web.json_response(
            {
                "message": "Formula already exists",
                "name": existing_formula.name,
            },
            status=409,
        )

    # attempt to save atomically
    successfully_saved = await publish_and_save(request.app, formula, materials_hash)
    if not successfully_saved:
        return web.json_response(
            {
                "error": "Failed to process formula after multiple attempts",
            },
            status=500,
        )

    return web.json_response({"message": "New formula received and added"}, status=201)


async def handle_get_formulas(request):
    formulas = await get_all_formulas()
    return web.json_response({"formulas": formulas}, status=200)


def setup_routes(app):
    app.router.add_post("/formulas", handle_create_formula)
    app.router.add_get("/formulas", handle_get_formulas)
