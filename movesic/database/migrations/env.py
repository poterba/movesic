import asyncio
from collections.abc import Iterable
import logging

from alembic import context
from alembic.environment import MigrationContext
from alembic.operations import MigrationScript
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from movesic.database import model

target_metadata = model.Base.metadata
config = context.config


def run_migrations_offline():
    # skip creation of empty migration if no changes
    def process_revision_directives(
        context: MigrationContext,
        revision: str | Iterable[str | None] | Iterable[str],
        directives: list[MigrationScript],
    ):
        print("process_revision_directives")
        assert config.cmd_opts is not None
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            assert script.upgrade_ops is not None
            if script.upgrade_ops.is_empty():
                directives[:] = []

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    try:
        with context.begin_transaction():
            context.run_migrations()
    except Exception as e:
        logging.error(f"Migration failed: {e}")

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)


def asyncio_run(future, as_task=True):
    def _to_task(future, as_task, loop):
        if not as_task or isinstance(future, asyncio.Task):
            return future
        return loop.create_task(future)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()

    return loop.run_until_complete(_to_task(future, as_task, loop))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
