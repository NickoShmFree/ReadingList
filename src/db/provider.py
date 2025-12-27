from typing import TYPE_CHECKING

from .services_db import (
    UserServiceDB,
    ReadingListServiceDB,
    ReadingListTagServiceDB,
    TagServiceDB,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Provider:
    """Провайдер для работы с БД"""

    session: "AsyncSession"

    user: UserServiceDB

    reading_list: ReadingListServiceDB
    tag: TagServiceDB
    reading_list_tag: ReadingListTagServiceDB

    def __init__(self, session: "AsyncSession") -> None:

        self.session = session

        self.user = UserServiceDB(self.session)

        self.reading_list = ReadingListServiceDB(self.session)
        self.tag = TagServiceDB(self.session)
        self.reading_list_tag = ReadingListTagServiceDB(self.session)
