from typing import TYPE_CHECKING

from .sa import SARepository
from db.models import UserDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo(SARepository[UserDB]):
    def __init__(self, session: "AsyncSession"):
        super().__init__(session=session, model_type=UserDB)
