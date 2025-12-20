import pytest

from movesic.database import init, session

_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def session_maker():
    init(_DB_URL)

    return session()
