from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic_ext import openapi

from app.exceptions import UserNotFoundError
from app.middleware import require_auth
from app.models import UserRole
from app.resources import AccountResource, PaymentResource, UserResource, to_json, to_json_list
from app.services import user_service

users_bp = Blueprint("users", url_prefix="/users")


@users_bp.get("/me")
@openapi.definition(response=UserResource, summary="Get my profile", tag="users", secured="token")
@require_auth(role=UserRole.USER)
async def me(request: Request):
    try:
        user = await user_service.get_profile(request.ctx.user_id)
    except UserNotFoundError:
        return json({"error": "User not found"}, status=404)

    return to_json(UserResource.model_validate(user))


@users_bp.get("/me/accounts")
@openapi.definition(response=[AccountResource], summary="List my accounts", tag="users", secured="token")
@require_auth(role=UserRole.USER)
async def my_accounts(request: Request):
    accounts = await user_service.list_accounts(request.ctx.user_id)
    return to_json_list([AccountResource.model_validate(a) for a in accounts])


@users_bp.get("/me/payments")
@openapi.definition(response=[PaymentResource], summary="List my payments", tag="users", secured="token")
@require_auth(role=UserRole.USER)
async def my_payments(request: Request):
    payments = await user_service.list_payments(request.ctx.user_id)
    return to_json_list([PaymentResource.model_validate(p) for p in payments])