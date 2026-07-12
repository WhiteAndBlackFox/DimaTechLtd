import asyncio
import os
import uuid

import pytest
from dotenv import load_dotenv

load_dotenv()

os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef"
os.environ["JWT_SECRET"] = "test-jwt-secret-0123456789abcdef"

@pytest.fixture(autouse=True)
def _reset_db():
    from app.db import Base, engine

    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_reset())
    yield


@pytest.fixture
def app():
    from app.factory import create_app

    return create_app(name=f"test-{uuid.uuid4().hex}")


@pytest.fixture
def seed():
    from app.db import async_session, engine

    def _seed(*objects):
        async def _persist():
            async with async_session() as session:
                session.add_all(objects)
                await session.commit()
                for obj in objects:
                    await session.refresh(obj)
            await engine.dispose()

        asyncio.run(_persist())
        return objects[0] if len(objects) == 1 else objects

    return _seed


@pytest.fixture
def auth_header():
    from app.helpers.auth import create_token

    def _auth_header(user_id: int, role: str) -> dict:
        return {"Authorization": f"Bearer {create_token(user_id, role)}"}

    return _auth_header