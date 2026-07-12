from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.factories import PaymentFactory
from app.models import Account, Payment


async def _get_or_create_payment(session: AsyncSession, account: Account, transaction_id: str) -> Payment:
    existing = (
        await session.execute(select(Payment).where(Payment.transaction_id == transaction_id))
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    payment = PaymentFactory(account=account, user=account.user, transaction_id=transaction_id)
    session.add(payment)
    await session.flush()
    return payment


async def seed_payments(session: AsyncSession, accounts: list[Account]) -> list[Payment]:
    payments = []
    for i, account in enumerate(accounts, start=1):
        transaction_id = f"seed-payment-{i:02d}"
        payments.append(await _get_or_create_payment(session, account, transaction_id))
    return payments