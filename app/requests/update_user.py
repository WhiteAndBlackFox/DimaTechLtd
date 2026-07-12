from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None