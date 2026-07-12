from sanic import Sanic

from app.db import close_db


def register_lifecycle(app: Sanic) -> None:
    @app.after_server_stop
    async def teardown_db(_app):
        await close_db()