import logging

from aiohttp import web

from app.db_models import init_db, drop_db
from app.event_queue import init_queue
from app.routes import setup_routes

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
_logger = logging.getLogger(__name__)


async def on_startup(app):
    """
    Application startup handler.
    Handles DB initialization and queue setup.
    """
    _logger.info("Starting up the application")
    # await drop_db()  # for testing purposes, drop existing tables
    await init_db()
    init_queue(app)


async def on_shutdown(app):
    _logger.info("Shutting down the application...")


def create_app():
    """
    Create and configure the aiohttp web application.
    """
    app = web.Application()
    setup_routes(app)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    """
    Run the aiohttp web application.
    """
    app = create_app()
    web.run_app(app, host="localhost", port=8080)
