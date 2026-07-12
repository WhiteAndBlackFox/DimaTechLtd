from sanic import Blueprint
from sanic.request import Request
from sanic.response import empty, json
from sanic_ext import openapi, validate

from app.exceptions import EmailAlreadyRegisteredError, UserNotFoundError
from app.middleware import require_auth
from app.models import UserRole
from app.requests import CreateUserRequest, UpdateUserRequest
from app.resources import UserResource, UserWithAccountsResource, to_json, to_json_list
from app.services import admin_service

admin_bp = Blueprint("admin", url_prefix="/admin")


@admin_bp.get("/me")
@openapi.definition(response=UserResource, summary="Get my profile", tag="admin", secured="token")
@require_auth(role=UserRole.ADMIN)
async def me(request: Request):
    try:
        user = await admin_service.get_profile(request.ctx.user_id)
    except UserNotFoundError:
        return json({"error": "User not found"}, status=404)

    return to_json(UserResource.model_validate(user))


@admin_bp.get("/users")
@openapi.definition(
    response=[UserWithAccountsResource], summary="List users with accounts", tag="admin", secured="token"
)
@require_auth(role=UserRole.ADMIN)
async def list_users(request: Request):
    users = await admin_service.list_users_with_accounts()
    return to_json_list([UserWithAccountsResource.model_validate(u) for u in users])


@admin_bp.post("/users")
@openapi.definition(
    body={"application/json": CreateUserRequest},
    response=UserResource,
    summary="Create user",
    tag="admin",
    secured="token",
)
@require_auth(role=UserRole.ADMIN)
@validate(json=CreateUserRequest)
async def create_user(request: Request, body: CreateUserRequest):
    try:
        user = await admin_service.create_user(body.email, body.full_name, body.password, body.role)
    except EmailAlreadyRegisteredError:
        return json({"error": "Email already registered"}, status=409)

    return to_json(UserResource.model_validate(user), status=201)


@admin_bp.put("/users/<user_id:int>")
@openapi.definition(
    body={"application/json": UpdateUserRequest},
    response=UserResource,
    summary="Update user",
    tag="admin",
    secured="token",
)
@require_auth(role=UserRole.ADMIN)
@validate(json=UpdateUserRequest)
async def update_user(request: Request, user_id: int, body: UpdateUserRequest):
    try:
        user = await admin_service.update_user(
            user_id,
            email=body.email,
            full_name=body.full_name,
            password=body.password,
            role=body.role,
            is_active=body.is_active,
        )
    except UserNotFoundError:
        return json({"error": "User not found"}, status=404)

    return to_json(UserResource.model_validate(user))


@admin_bp.delete("/users/<user_id:int>")
@openapi.definition(summary="Delete user", tag="admin", secured="token")
@require_auth(role=UserRole.ADMIN)
async def delete_user(request: Request, user_id: int):
    try:
        await admin_service.delete_user(user_id)
    except UserNotFoundError:
        return json({"error": "User not found"}, status=404)

    return empty()