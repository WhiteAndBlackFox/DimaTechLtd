from pydantic import BaseModel
from sanic.response import HTTPResponse
from sanic.response import json as json_response

from app.resources.account import AccountResource
from app.resources.payment import PaymentResource
from app.resources.token import TokenResource
from app.resources.user import UserResource
from app.resources.user_with_accounts import UserWithAccountsResource
from app.resources.webhook_result import WebhookResultResource

__all__ = [
    "UserResource",
    "UserWithAccountsResource",
    "AccountResource",
    "PaymentResource",
    "TokenResource",
    "WebhookResultResource",
    "to_json",
    "to_json_list",
]


def to_json(resource: BaseModel, status: int = 200) -> HTTPResponse:
    return json_response(resource.model_dump(mode="json"), status=status)


def to_json_list(resources: list[BaseModel], status: int = 200) -> HTTPResponse:
    return json_response([resource.model_dump(mode="json") for resource in resources], status=status)