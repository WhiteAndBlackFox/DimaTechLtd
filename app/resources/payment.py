from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentResource(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    account_id: int
    amount: float
    created_at: datetime