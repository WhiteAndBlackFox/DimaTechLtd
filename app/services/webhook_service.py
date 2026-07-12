from decimal import Decimal

from sqlalchemy import select

from app.db import async_session
from app.exceptions import AccountOwnershipError, InvalidSignatureError, UserNotFoundError
from app.models import Account, Payment, User
from app.helpers.signature import verify_signature


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

        account = await session.get(Account, account_id)
        if account is not None and account.user_id != user_id:
            raise AccountOwnershipError

        if account is None:
            account = Account(id=account_id, user_id=user_id, balance=Decimal("0"))
            session.add(account)
            await session.flush()

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
        await session.commit()

    return "ok"