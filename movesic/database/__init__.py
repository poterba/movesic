from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


_engine = None
async_session_maker = None

@asynccontextmanager
async def session() -> AsyncGenerator[AsyncSession]:
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()

def init(url):
    global _engine
    global async_session_maker
    _engine = create_async_engine(url)
    async_session_maker = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        autoflush=True,
    )
    logging.info("database initialized")
