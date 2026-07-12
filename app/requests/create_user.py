from pydantic import BaseModel

from app.models import UserRole


class CreateUserRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = UserRole.USER