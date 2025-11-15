from aiohttp import web
from app.routes import setup_routes


def create_app():
    app = web.Application()
    setup_routes(app)
    # startup logic here
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="localhost", port=8080)
