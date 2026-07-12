from sanic import Sanic

from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.webhook import webhook_bp


def register_blueprints(app: Sanic) -> None:
    app.blueprint(auth_bp)
    app.blueprint(users_bp)
    app.blueprint(admin_bp)
    app.blueprint(webhook_bp)