from typing import TYPE_CHECKING, AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from cfg.db import db_cfg
from .provider import Provider

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


class ConnectionManager(object):
    """Коннектор к БД"""

    _instance: "ConnectionManager"

    engine: Optional["AsyncEngine"] = None
    session_factory: async_sessionmaker | None = None

    def __new__(cls) -> "ConnectionManager":
        if not getattr(cls, "_instance", False):
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self.engine is None:
            self.engine = create_async_engine(
                db_cfg.conn_string,
                pool_size=db_cfg.pool_size,
                max_overflow=db_cfg.max_overflow,
                pool_timeout=db_cfg.pool_timeout,
            )
        if self.session_factory is None:
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=db_cfg.expire_on_commit,
            )

    async def disconnect(self):
        if self.engine is not None:
            await self.engine.dispose()


@asynccontextmanager
async def build_provider():
    manager = ConnectionManager()
    if manager.session_factory is None:
        raise RuntimeError("Session factory initialization failed.")
    provider = Provider(manager.session_factory())
    try:
        yield provider
    except Exception as ex:
        await provider.session.rollback()
        raise (ex)
    finally:
        await provider.session.close()


async def get_provider() -> AsyncGenerator[Provider, None]:
    async with build_provider() as provider:
        yield provider
