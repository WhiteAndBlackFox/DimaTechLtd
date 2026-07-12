from sqlalchemy import select

from app.db import async_session
from app.exceptions import UserNotFoundError
from app.models import Account, Payment, User


async def get_profile(user_id: int) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)

    if user is None:
        raise UserNotFoundError

    return user


async def list_accounts(user_id: int) -> list[Account]:
    async with async_session() as session:
        result = await session.execute(select(Account).where(Account.user_id == user_id))
        return list(result.scalars().all())


async def list_payments(user_id: int) -> list[Payment]:
    async with async_session() as session:
        result = await session.execute(select(Payment).where(Payment.user_id == user_id))
        return list(result.scalars().all())