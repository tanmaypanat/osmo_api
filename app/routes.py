import aiohttp.web as web


async def handle_create_formula(request):
    return web.json_response({"status": "formula created"}, status=201)


def setup_routes(app):
    app.router.add_post("/formulas", handle_create_formula)
