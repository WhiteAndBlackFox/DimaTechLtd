from pydantic import BaseModel


class WebhookPaymentRequest(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: float
    signature: str