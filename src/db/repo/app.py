from typing import TYPE_CHECKING

from .sa import SARepository
from db.models import UserDB, ReadingListDB, TagDB, ReadingListTagDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo(SARepository[UserDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=UserDB)


class ReadingListRepo(SARepository[ReadingListDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=ReadingListDB)


class TagRepo(SARepository[TagDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=TagDB)


class ReadingListTagRepo(SARepository[ReadingListTagDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=ReadingListTagDB)
