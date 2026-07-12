import asyncio
import uuid

import pytest_asyncio
from sqlalchemy import select

from app.db import async_session, engine
from app.factories import AccountFactory, UserFactory
from app.helpers.signature import build_signature
from app.models import Account, Payment
from app.services.webhook_service import process_payment


@pytest_asyncio.fixture(autouse=True)
async def _dispose_engine_after_test():
    yield
    await engine.dispose()


async def _create_user() -> int:
    async with async_session() as session:
        user = UserFactory(email=f"concurrency-{uuid.uuid4()}@example.com")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.id


async def _create_user_with_account(balance=0) -> tuple[int, int]:
    async with async_session() as session:
        user = UserFactory(email=f"concurrency-{uuid.uuid4()}@example.com")
        account = AccountFactory(user=user, balance=balance)
        session.add_all([user, account])
        await session.commit()
        await session.refresh(user)
        await session.refresh(account)
        return user.id, account.id


async def _credit(account_id: int, user_id: int, amount, transaction_id: str) -> str:
    signature = build_signature(account_id, amount, transaction_id, user_id)
    return await process_payment(
        transaction_id=transaction_id,
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        signature=signature,
    )


async def test_concurrent_webhooks_do_not_lose_balance_updates():
    user_id, account_id = await _create_user_with_account(balance=0)

    n, amount = 20, 10
    tx_ids = [f"concurrent-{uuid.uuid4()}" for _ in range(n)]

    results = await asyncio.gather(*(_credit(account_id, user_id, amount, tx) for tx in tx_ids))
    assert results == ["ok"] * n

    async with async_session() as session:
        account = await session.get(Account, account_id)
        payments = (
            await session.execute(select(Payment).where(Payment.account_id == account_id))
        ).scalars().all()

    assert account.balance == n * amount
    assert len(payments) == n


async def test_concurrent_webhooks_creating_the_same_new_account_do_not_race():
    user_id = await _create_user()
    new_account_id = 900_000_000 + user_id  # guaranteed to not exist yet

    n, amount = 10, 5
    tx_ids = [f"newacc-{uuid.uuid4()}" for _ in range(n)]

    results = await asyncio.gather(*(_credit(new_account_id, user_id, amount, tx) for tx in tx_ids))
    assert results == ["ok"] * n

    async with async_session() as session:
        account = await session.get(Account, new_account_id)
        payments = (
            await session.execute(select(Payment).where(Payment.account_id == new_account_id))
        ).scalars().all()

    assert account.balance == n * amount
    assert len(payments) == n


async def test_concurrent_duplicate_transaction_id_credits_only_once():
    user_id, account_id = await _create_user_with_account(balance=0)
    tx_id = f"dup-{uuid.uuid4()}"
    amount = 42

    results = await asyncio.gather(*(_credit(account_id, user_id, amount, tx_id) for _ in range(10)))

    assert results.count("ok") == 1
    assert results.count("already processed") == 9

    async with async_session() as session:
        account = await session.get(Account, account_id)
        payments = (
            await session.execute(select(Payment).where(Payment.account_id == account_id))
        ).scalars().all()

    assert account.balance == amount
    assert len(payments) == 1