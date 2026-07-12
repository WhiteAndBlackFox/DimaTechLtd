from sanic import Sanic

from app.db import close_db


def create_app(name: str = "dima_tech_ltd") -> Sanic:
    app = Sanic(name)

    _register_lifecycle(app)

    return app


def _register_lifecycle(app: Sanic) -> None:
    @app.after_server_stop
    async def teardown_db(_app, _loop):
        await close_db()