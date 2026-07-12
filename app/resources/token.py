from pydantic import BaseModel


class TokenResource(BaseModel):
    token: str