from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.factories import AdminFactory, UserFactory
from app.helpers.auth import hash_password
from app.models import User

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "12345!admin54321"

USER_COUNT = 10
DEFAULT_USER_PASSWORD = "12345!user54321"


async def _get_or_create_user(
    session: AsyncSession, factory_cls, email: str, full_name: str, password: str
) -> User:
    existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is not None:
        return existing

    user = factory_cls(email=email, full_name=full_name, hashed_password=hash_password(password))
    session.add(user)
    await session.flush()
    return user


async def seed_users(session: AsyncSession) -> list[User]:
    await _get_or_create_user(session, AdminFactory, ADMIN_EMAIL, "Test Admin", ADMIN_PASSWORD)

    users = []
    for i in range(1, USER_COUNT + 1):
        email = "user@example.com" if i == 1 else f"user{i:02d}@example.com"
        full_name = "Test User" if i == 1 else f"Test User {i:02d}"
        user = await _get_or_create_user(session, UserFactory, email, full_name, DEFAULT_USER_PASSWORD)
        users.append(user)

    return users