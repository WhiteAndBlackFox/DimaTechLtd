from pydantic import BaseModel, ConfigDict


class AccountResource(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    balance: float