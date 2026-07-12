import asyncio
import atexit
import os
import tempfile
import uuid

_tmp_db_fd, _tmp_db_path = tempfile.mkstemp(suffix=".db")
os.close(_tmp_db_fd)
atexit.register(lambda: os.path.exists(_tmp_db_path) and os.remove(_tmp_db_path))

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_tmp_db_path}")
os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-0123456789abcdef")

import pytest

from app.helpers.auth import create_token
from app.db import Base, async_session, engine
from app.factory import create_app


@pytest.fixture(autouse=True)
def _reset_db():
    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_reset())
    yield


@pytest.fixture
def app():
    return create_app(name=f"test-{uuid.uuid4().hex}")


@pytest.fixture
def seed():
    def _seed(*objects):
        async def _persist():
            async with async_session() as session:
                session.add_all(objects)
                await session.commit()
                for obj in objects:
                    await session.refresh(obj)

        asyncio.run(_persist())
        return objects[0] if len(objects) == 1 else objects

    return _seed


@pytest.fixture
def auth_header():
    def _auth_header(user_id: int, role: str) -> dict:
        return {"Authorization": f"Bearer {create_token(user_id, role)}"}

    return _auth_header