import pytest
import sqlalchemy
from pytest_alembic.tests import (
    test_model_definitions_match_ddl,  # noqa: F401
    test_single_head_revision,  # noqa: F401
    test_up_down_consistency,  # noqa: F401
    test_upgrade,  # noqa: F401
)

SQLALCHEMY_DATABASE_URL = "sqlite://"


@pytest.fixture
def alembic_config():
    return {
        "file": "alembic.ini",
        "script_location": "movesic/database/migrations",
    }


@pytest.fixture
def alembic_engine():
    engine = sqlalchemy.create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=sqlalchemy.StaticPool,
    )
    return engine.connect()
