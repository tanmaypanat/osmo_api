from aiohttp import web
from app.routes import setup_routes
from app.db_models import init_db
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_logger = logging.getLogger(__name__)


async def on_startup(app):
    _logger.info("Starting up the application...")
    await init_db()


async def on_shutdown(app):
    _logger.info("Shutting down the application...")


def create_app():
    app = web.Application()
    setup_routes(app)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="localhost", port=8080)
