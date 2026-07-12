from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.exceptions import AccountOwnershipError, InvalidSignatureError, UserNotFoundError
from app.helpers.signature import verify_signature
from app.models import Account, Payment, User


async def _get_locked_account(session: AsyncSession, account_id: int, user_id: int) -> Account:
    account = (
        await session.execute(select(Account).where(Account.id == account_id).with_for_update())
    ).scalar_one_or_none()

    if account is not None:
        if account.user_id != user_id:
            raise AccountOwnershipError
        return account

    account = Account(id=account_id, user_id=user_id, balance=Decimal("0"))
    session.add(account)
    try:
        await session.flush()
    except IntegrityError:
        # lost the race to create this account someone else just created it, take its lock instead
        await session.rollback()
        account = (
            await session.execute(select(Account).where(Account.id == account_id).with_for_update())
        ).scalar_one_or_none()
        if account is None:
            raise
        if account.user_id != user_id:
            raise AccountOwnershipError from None

    return account


async def process_payment(
    *, transaction_id: str, user_id: int, account_id: int, amount: int | float, signature: str
) -> str:
    if not verify_signature(
        account_id=account_id,
        amount=amount,
        transaction_id=transaction_id,
        user_id=user_id,
        signature=signature,
    ):
        raise InvalidSignatureError

    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise UserNotFoundError

        existing_payment = (
            await session.execute(select(Payment).where(Payment.transaction_id == transaction_id))
        ).scalar_one_or_none()
        if existing_payment is not None:
            return "already processed"

        # row lock serializes concurrent webhook deliveries for the same account,
        # preventing a lost balance update when two payments arrive at once
        account = await _get_locked_account(session, account_id, user_id)

        credited_amount = Decimal(str(amount))
        account.balance += credited_amount
        session.add(
            Payment(
                transaction_id=transaction_id,
                user_id=user_id,
                account_id=account.id,
                amount=credited_amount,
            )
        )
        try:
            await session.commit()
        except IntegrityError:
            # another concurrent delivery of the same transaction_id won the race and already committed
            await session.rollback()
            return "already processed"

    return "ok"