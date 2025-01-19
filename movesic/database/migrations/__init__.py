import logging
from pathlib import Path

from alembic import command
from alembic.config import Config


def run_migrations(db_url=None) -> None:
    if not db_url:
        from movesic.config import MovesicConfig

        db_url = MovesicConfig.DATABASE_URL

    script_location = str(Path(__file__).parent)

    logging.info(f"Running DB migrations in {script_location}")

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")

    logging.info("Successfully migrated")
