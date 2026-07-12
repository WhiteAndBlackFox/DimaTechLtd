from sqlalchemy import select

from app.helpers.auth import create_token, verify_password
from app.db import async_session
from app.exceptions import InvalidCredentialsError
from app.models import User


async def login(email: str, password: str) -> str:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError

    return create_token(user.id, user.role)