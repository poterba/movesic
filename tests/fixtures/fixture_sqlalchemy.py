import asyncio

import pytest

from movesic.database import database_init, model, recreate, session

_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def session_maker():
    database_init(_DB_URL)

    asyncio.run(recreate(model.Base))

    return session()
