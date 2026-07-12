from pydantic import BaseModel, ConfigDict

from app.resources.account import AccountResource


class UserWithAccountsResource(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    accounts: list[AccountResource]