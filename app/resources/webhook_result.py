from pydantic import BaseModel


class WebhookResultResource(BaseModel):
    status: str