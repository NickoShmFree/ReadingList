from typing import TYPE_CHECKING

from .services_db import UserServiceDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Provider:
    """Провайдер для работы с БД"""

    session: "AsyncSession"

    user: UserServiceDB

    def __init__(self, session: "AsyncSession") -> None:

        self.session = session

        self.user = UserServiceDB(self.session)
