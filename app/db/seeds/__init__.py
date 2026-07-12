import asyncio

from app.db import async_session
from app.db.seeds.accounts import seed_accounts
from app.db.seeds.payments import seed_payments
from app.db.seeds.users import seed_users


async def run() -> None:
    async with async_session() as session:
        users = await seed_users(session)
        accounts = await seed_accounts(session, users)
        await seed_payments(session, accounts)
        await session.commit()


def main() -> None:
    asyncio.run(run())