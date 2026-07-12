from pydantic import BaseModel, ConfigDict


class UserResource(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str