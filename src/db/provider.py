from typing import TYPE_CHECKING

from .services_db import (
    UserServiceDB,
    ItemServiceDB,
    ItemTagServiceDB,
    TagServiceDB,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Provider:
    """Провайдер для работы с БД"""

    session: "AsyncSession"

    user: UserServiceDB

    reading_list: ItemServiceDB
    tag: TagServiceDB
    reading_list_tag: ItemTagServiceDB

    def __init__(self, session: "AsyncSession") -> None:

        self.session = session

        self.user = UserServiceDB(self.session)

        self.reading_list = ItemServiceDB(self.session)
        self.tag = TagServiceDB(self.session)
        self.reading_list_tag = ItemTagServiceDB(self.session)
