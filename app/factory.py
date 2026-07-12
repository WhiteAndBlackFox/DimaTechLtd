from sanic import Sanic
from sanic_ext import Extend

from app.lifecycle import register_lifecycle
from app.routes import register_blueprints


def create_app(name: str = "dima_tech_ltd") -> Sanic:
    app = Sanic(name)

    app.config.OAS_UI_DEFAULT = "swagger"
    Extend(app)
    app.ext.openapi.add_security_scheme("token", "http", scheme="bearer", bearer_format="JWT")

    register_blueprints(app)
    register_lifecycle(app)

    return app