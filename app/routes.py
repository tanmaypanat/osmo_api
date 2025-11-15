import hashlib
import logging
import re

import aiohttp.web as web
from pydantic import ValidationError

from app.db_models import add_formula, check_formula_exists
from app.schemas import Formulation, Material

_logger = logging.getLogger(__name__)


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
    print(materials_hash)
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

    return web.json_response({"message": "New formula received and added"}, status=201)


def setup_routes(app):
    app.router.add_post("/formulas", handle_create_formula)
