from typing import TYPE_CHECKING

from .sa import SARepository
from db.models import UserDB, ItemDB, TagDB, ItemTagDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo(SARepository[UserDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=UserDB)


class ItemRepo(SARepository[ItemDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=ItemDB)


class TagRepo(SARepository[TagDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=TagDB)


class ItemTagRepo(SARepository[ItemTagDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=ItemTagDB)
