from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.factories import AccountFactory
from app.models import Account, User


async def _get_or_create_account(session: AsyncSession, user: User) -> Account:
    existing = (await session.execute(select(Account).where(Account.user_id == user.id))).scalar_one_or_none()
    if existing is not None:
        return existing

    account = AccountFactory(user=user, balance=0)
    session.add(account)
    await session.flush()
    return account


async def seed_accounts(session: AsyncSession, users: list[User]) -> list[Account]:
    return [await _get_or_create_account(session, user) for user in users]