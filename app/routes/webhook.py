from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic_ext import openapi, validate

from app.exceptions import AccountOwnershipError, InvalidSignatureError, UserNotFoundError
from app.requests import WebhookPaymentRequest
from app.resources import WebhookResultResource, to_json
from app.services import webhook_service

webhook_bp = Blueprint("webhook", url_prefix="/webhook")


@webhook_bp.post("/payment")
@openapi.definition(
    body={"application/json": WebhookPaymentRequest},
    response=WebhookResultResource,
    summary="Process a payment webhook",
    tag="webhook",
)
@validate(json=WebhookPaymentRequest)
async def process_payment(request: Request, body: WebhookPaymentRequest):
    try:
        status = await webhook_service.process_payment(
            transaction_id=body.transaction_id,
            user_id=body.user_id,
            account_id=body.account_id,
            amount=request.json["amount"],
            signature=body.signature,
        )
    except InvalidSignatureError:
        return json({"error": "Invalid signature"}, status=400)
    except UserNotFoundError:
        return json({"error": "User not found"}, status=404)
    except AccountOwnershipError:
        return json({"error": "Account does not belong to user"}, status=400)

    return to_json(WebhookResultResource(status=status))