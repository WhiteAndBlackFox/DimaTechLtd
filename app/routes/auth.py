from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic_ext import openapi, validate

from app.exceptions import InvalidCredentialsError
from app.requests import LoginRequest
from app.resources import TokenResource, to_json
from app.services import auth_service

auth_bp = Blueprint("auth", url_prefix="/auth")


@auth_bp.post("/login")
@openapi.definition(
    body={"application/json": LoginRequest}, response=TokenResource, summary="Login", tag="auth"
)
@validate(json=LoginRequest)
async def login(request: Request, body: LoginRequest):
    try:
        token = await auth_service.login(body.email, body.password)
    except InvalidCredentialsError:
        return json({"error": "Invalid credentials"}, status=401)

    return to_json(TokenResource(token=token))