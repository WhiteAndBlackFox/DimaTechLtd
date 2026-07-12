from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import async_session
from app.exceptions import EmailAlreadyRegisteredError, UserNotFoundError
from app.helpers.auth import hash_password
from app.models import User


async def get_profile(user_id: int) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)

    if user is None:
        raise UserNotFoundError

    return user


async def list_users_with_accounts() -> list[User]:
    async with async_session() as session:
        result = await session.execute(select(User).options(selectinload(User.accounts)))
        return list(result.scalars().all())


async def create_user(email: str, full_name: str, password: str, role: str) -> User:
    async with async_session() as session:
        existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if existing is not None:
            raise EmailAlreadyRegisteredError

        user = User(email=email, full_name=full_name, hashed_password=hash_password(password), role=role)
        session.add(user)
        await session.commit()

        return user


async def update_user(
    user_id: int,
    *,
    email: str | None,
    full_name: str | None,
    password: str | None,
    role: str | None,
    is_active: bool | None,
) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise UserNotFoundError

        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if password is not None:
            user.hashed_password = hash_password(password)
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        await session.commit()

        return user


async def delete_user(user_id: int) -> None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise UserNotFoundError

        await session.delete(user)
        await session.commit()