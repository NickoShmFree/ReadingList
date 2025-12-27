from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio.session import AsyncSession

from db.repo.app import ReadingListRepo
from db.models import ReadingListDB

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from schemas import ReadingListResponseSchema


class ReadingListServiceDB:
    """Сервис для работы с таблицей users (пользователи)"""

    def __init__(self, session: "AsyncSession") -> None:
        self.repo = ReadingListRepo(session)

    async def add(
        self,
        user_id: int,
        reading_list: "ReadingListResponseSchema",
    ) -> ReadingListDB:
        model = ReadingListDB(
            user_id=user_id,
            title=reading_list.title,
            kind=reading_list.kind,
            status=reading_list.status,
            priority=reading_list.priority,
            notes=reading_list.notes,
        )
        await self.repo.add(model=model)
        return model
